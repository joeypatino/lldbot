import json
import urllib
from urllib.request import Request

from config_manager import ConfigManager
from source_kitten import is_swift_file, get_structure, extract_function
from spinner import Spinner


class ExplainCommand(object):
    def __init__(self, subOptions, debugger, exe_ctx, result):
        self.configManager = ConfigManager()
        self.subOptions = subOptions
        self.debugger = debugger
        self.exe_ctx = exe_ctx
        self.result = result
        self.run()

    def run(self):
        api_key = self.configManager.get_api_token() or self.subOptions.api_key
        if not api_key:  # if api_key is not given
            self.result.SetError("missing api token")
            return

        # Always get program state from the lldb.SBExecutionContext passed
        # in as exe_ctx
        frame = self.exe_ctx.GetFrame()
        if not frame.IsValid():
            self.result.SetError("invalid frame")
            return

        # Get the variables in the current stack frame
        variables_list = frame.GetVariables(
            self.subOptions.arguments,
            self.subOptions.locals,
            self.subOptions.statics,
            self.subOptions.inscope)

        thread = self.debugger.GetSelectedTarget().GetProcess().GetSelectedThread()

        stacktrace = ''
        # Iterate over the variables
        for i in range(variables_list.GetSize()):
            var = variables_list.GetValueAtIndex(i)
            if var.GetName() == 'exception':
                stacktrace += f'{var.GetSummary()}\n'

        # Get the backtrace
        for i in range(thread.GetNumFrames()):
            frame = thread.GetFrameAtIndex(i)

            # Get the line entry for this frame
            line_entry = frame.GetLineEntry()

            # Get the file spec for the line entry
            file_spec = line_entry.GetFileSpec()

            # Get the file path
            if file_spec == None: continue
            if file_spec.GetDirectory() == None: continue
            if file_spec.GetFilename() == None: continue

            file_path = file_spec.GetDirectory() + '/' + file_spec.GetFilename()
            if is_swift_file(file_path) == False: continue
            fn_info = json.loads(get_structure(file_path, frame.GetDisplayFunctionName()))

            for i in range(len(fn_info)):
                stacktrace += extract_function(file_path, fn_info[i]['start'], fn_info[i]['end'])

        data = {
            "model": "text-davinci-003",
            "prompt": f"Given the following Xcode Stack strace, find the cause of the crash and a list the steps required to fix it. You should ignore all lines of code that are commented out:\n%{stacktrace}",
            "temperature": 0,
            "max_tokens": 300,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }
        req = Request('https://api.openai.com/v1/completions', data=json.dumps(data).encode(),
                      headers=headers)

        spinner = Spinner(message='Analyzing...', delay=0.1)
        spinner.start()
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())

        spinner.stop()

        if res is not None:
            choices = res['choices'] or []
            if len(choices) == 0:
                self.result.SetError("No response")
            else:
                print(res['choices'][0]['text'])
        else:
            self.result.SetError("No response")
