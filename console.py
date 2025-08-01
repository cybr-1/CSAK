import os
import sys
import re
import subprocess
import cmd2
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

SCRIPTS_DIR = "./modules"

class MyConsole(cmd2.Cmd):
    def __init__(self):
        super().__init__()
        self.current_module = None
        self.current_script = None
        self.script_params = {}
        self.script_options = {}
        self.update_prompt()

    def update_prompt(self):
        if self.current_script:
            self.prompt = f"secops toolkit ({Fore.YELLOW}{self.current_module}{Style.RESET_ALL}) - {Fore.RED}{self.current_script}{Style.RESET_ALL} > "
        elif self.current_module:
            self.prompt = f"secops toolkit ({Fore.YELLOW}{self.current_module}{Style.RESET_ALL}) > "
        else:
            self.prompt = "secops toolkit > "

    def do_list(self, args):
        args = args.strip().lower()
        if args == "modules":
            self.list_modules()
        elif args == "tools":
            self.list_tools()
        elif not args:
            self.list_all()
        else:
            print(f"{Fore.RED}Invalid command. Use 'list', 'list modules', or 'list tools'.{Style.RESET_ALL}")

    def list_all(self):
        if not os.path.exists(SCRIPTS_DIR):
            print(f"{Fore.RED}Scripts directory not found: {SCRIPTS_DIR}{Style.RESET_ALL}")
            return

        modules = [d for d in os.listdir(SCRIPTS_DIR) if os.path.isdir(os.path.join(SCRIPTS_DIR, d))]
        if not modules:
            print(f"{Fore.RED}No modules found in {SCRIPTS_DIR}{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}Available Modules and Tools:{Style.RESET_ALL}\n")
        for module in sorted(modules):
            module_desc = self.get_module_description(module)
            print(f"{Fore.YELLOW}Module: {module}{Style.RESET_ALL} - {module_desc}")

            module_path = os.path.join(SCRIPTS_DIR, module)
            scripts = [f[:-3] for f in os.listdir(module_path) if f.endswith(".py")]

            if not scripts:
                print(f"  {Fore.YELLOW}No tools in this module{Style.RESET_ALL}\n")
            else:
                for script in sorted(scripts):
                    tool_desc = self.get_tool_description(module, script)
                    print(f"  {Fore.GREEN}↳ {script}{Style.RESET_ALL} - {tool_desc}")
                print("")

    def list_modules(self):
        if not os.path.exists(SCRIPTS_DIR):
            print(f"{Fore.RED}Scripts directory not found: {SCRIPTS_DIR}{Style.RESET_ALL}")
            return

        modules = [d for d in os.listdir(SCRIPTS_DIR) if os.path.isdir(os.path.join(SCRIPTS_DIR, d))]
        if not modules:
            print(f"{Fore.RED}No modules found in {SCRIPTS_DIR}{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}Available Modules:{Style.RESET_ALL}\n")
        for module in sorted(modules):
            desc = self.get_module_description(module)
            print(f"  - {Fore.YELLOW}{module}{Style.RESET_ALL} - {desc}")
        print("")

    def list_tools(self):
        if not self.current_module:
            print(f"{Fore.RED}No module selected. Use 'use module <module>' first.{Style.RESET_ALL}")
            return

        module_path = os.path.join(SCRIPTS_DIR, self.current_module)
        scripts = [f[:-3] for f in os.listdir(module_path) if f.endswith(".py")]

        if not scripts:
            print(f"{Fore.RED}No tools found in module {self.current_module}.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}Available Tools in {self.current_module}:{Style.RESET_ALL}\n")
        for script in sorted(scripts):
            desc = self.get_tool_description(self.current_module, script)
            print(f"  - {Fore.GREEN}{script}{Style.RESET_ALL} - {desc}")
        print("")

    def get_module_description(self, module_name):
        for filename in ["README.md", "description.txt"]:
            path = os.path.join(SCRIPTS_DIR, module_name, filename)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    for line in f:
                        if line.strip():
                            return line.strip()
        return "No description available"

    def get_tool_description(self, module_name, tool_name):
        path = os.path.join(SCRIPTS_DIR, module_name, f"{tool_name}.py")
        if not os.path.exists(path):
            return "No description available"

        try:
            with open(path, 'r') as f:
                content = f.read()
            docstring = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring:
                return docstring.group(1).strip().split("\n")[0]
            desc_match = re.search(r'description=["\'](.+?)["\']', content)
            return desc_match.group(1) if desc_match else "No description available"
        except:
            return "No description available"

if __name__ == "__main__":
    console = MyConsole()
    console.cmdloop()
