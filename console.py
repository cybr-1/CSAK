import os
import cmd2
import subprocess
import sys
import time
import itertools
import re
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Base directory for scripts
SCRIPTS_DIR = "./modules"

def loading_sequence():
    """Display a loading animation."""
    os.system("cls" if os.name == "nt" else "clear")
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    for _ in range(30):  
        sys.stdout.write(f"\r{Fore.GREEN}Loading {next(spinner)} {Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.1)

    os.system("cls" if os.name == "nt" else "clear")

    print(f"{Fore.GREEN}The Matrix has you...\n\nFollow the white rabbit...\n\nKnock knock, Neo.\n-----------------\n{Style.RESET_ALL}")
    time.sleep(1)

class MyConsole(cmd2.Cmd):
    def __init__(self):
        super().__init__()
        self.current_module = None
        self.current_script = None
        self.script_params = {}  # Stores user-set parameters
        self.script_options = {}  # Stores available options for the current script
        self.update_prompt()

    def update_prompt(self):
        """Update the console prompt dynamically."""
        if self.current_script:
            self.prompt = f"secops toolkit ({Fore.YELLOW}{self.current_module}{Style.RESET_ALL}) - {Fore.RED}{self.current_script}{Style.RESET_ALL} > "
        elif self.current_module:
            self.prompt = f"secops toolkit ({Fore.YELLOW}{self.current_module}{Style.RESET_ALL}) > "
        else:
            self.prompt = "secops toolkit > "

    def do_list(self, args):
        """List modules or tools."""
        args = args.strip().lower()
        if args == "modules":
            self.list_modules()
        elif args == "tools":
            self.list_tools()
        elif not args:  # If no arguments, show everything
            self.list_all()
        else:
            print(f"{Fore.RED}Invalid command. Use 'list', 'list modules', or 'list tools'.{Style.RESET_ALL}")

    def list_all(self):
        """List all modules and their tools."""
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
            print(f"{Fore.YELLOW}Module: {module} {Style.RESET_ALL}- {module_desc}")
            
            # List tools in this module
            module_path = os.path.join(SCRIPTS_DIR, module)
            scripts = [f[:-3] for f in os.listdir(module_path) if f.endswith(".py")]
            
            if not scripts:
                print(f"  {Fore.YELLOW}No tools in this module{Style.RESET_ALL}\n")
            else:
                for script in sorted(scripts):
                    tool_desc = self.get_tool_description(module, script)
                    print(f"  {Fore.GREEN}↳ {script}{Style.RESET_ALL} - {tool_desc}")
                print("")  # Extra line for better readability

    def list_modules(self):
        """List available modules."""
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
        """List scripts inside the selected module."""
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
        """Get the description for a module."""
        # First check for a README.md in the module directory
        readme_path = os.path.join(SCRIPTS_DIR, module_name, "README.md")
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r') as f:
                    # Read the first line or first paragraph as the description
                    desc = f.readline().strip()
                    if not desc and f.readable():  # If first line is empty, read next line
                        desc = f.readline().strip()
                    return desc if desc else "No description available"
            except:
                pass
        
        # Check for description.txt as an alternative
        desc_path = os.path.join(SCRIPTS_DIR, module_name, "description.txt")
        if os.path.exists(desc_path):
            try:
                with open(desc_path, 'r') as f:
                    return f.readline().strip()
            except:
                pass
        
        # Fall back to default description
        return "No description available"

    def get_tool_description(self, module_name, tool_name):
        """Get the description for a tool by examining its docstring."""
        script_path = os.path.join(SCRIPTS_DIR, module_name, f"{tool_name}.py")
        
        if not os.path.exists(script_path):
            return "No description available"
        
        try:
            # Read the file to look for docstring or description comment
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Look for triple-quoted docstring
            docstring_pattern = r'"""(.*?)"""'
            docstring_match = re.search(docstring_pattern, content, re.DOTALL)
            
            if docstring_match:
                # Extract the first line or sentence from the docstring
                docstring = docstring_match.group(1).strip()
                first_line = docstring.split("\n")[0].strip()
                return first_line if first_line else "No description available"
            
            # Look for help text in argparse if no docstring found
            parser_help_pattern = r'ArgumentParser\(.*?description=[\'"](.+?)[\'"]'
            parser_help_match = re.search(parser_help_pattern, content, re.DOTALL)
            
            if parser_help_match:
                return parser_help_match.group(1)
            
            return "No description available"
        except:
            return "No description available"

    def do_use(self, args):
        """Use a module or tool."""
        parts = args.strip().split()
        if len(parts) < 2:
            print(f"{Fore.RED}Invalid command. Use 'use module <module_name>' or 'use tool <tool_name>'.{Style.RESET_ALL}")
            return

        command, name = parts[0], " ".join(parts[1:])  # Supports names with spaces if needed

        if command == "module":
            self.use_module(name)
        elif command == "tool":
            self.use_tool(name)
        else:
            print(f"{Fore.RED}Invalid usage. Use 'use module <module_name>' or 'use tool <tool_name>'.{Style.RESET_ALL}")

    def use_module(self, module_name):
        """Select a module."""
        module_path = os.path.join(SCRIPTS_DIR, module_name)
        if os.path.exists(module_path) and os.path.isdir(module_path):
            self.current_module = module_name
            self.current_script = None
            self.script_params = {}
            self.script_options = {}
            self.update_prompt()
            print(f"Selected module: {Fore.YELLOW}{module_name}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Module '{module_name}' not found.{Style.RESET_ALL}")

    def use_tool(self, script_name):
        """Select a tool by searching through all modules."""
        # If a module is already selected, first check there
        if self.current_module:
            script_path = os.path.join(SCRIPTS_DIR, self.current_module, f"{script_name}.py")
            if os.path.exists(script_path):
                self.current_script = script_name
                self.script_params = {}
                self.script_options = {}
                self.update_prompt()
                print(f"Selected tool: {Fore.GREEN}{script_name}{Style.RESET_ALL} from module {Fore.YELLOW}{self.current_module}{Style.RESET_ALL}")
                self.parse_tool_options()
                return

        # If we get here, either no module was selected or the tool wasn't found in the current module
        # Search through all modules
        found_modules = []
        
        if os.path.exists(SCRIPTS_DIR):
            modules = [d for d in os.listdir(SCRIPTS_DIR) if os.path.isdir(os.path.join(SCRIPTS_DIR, d))]
            
            for module in modules:
                script_path = os.path.join(SCRIPTS_DIR, module, f"{script_name}.py")
                if os.path.exists(script_path):
                    found_modules.append(module)
        
        if not found_modules:
            print(f"{Fore.RED}Tool '{script_name}' not found in any module.{Style.RESET_ALL}")
            return
        
        if len(found_modules) > 1:
            print(f"{Fore.YELLOW}Tool '{script_name}' found in multiple modules: {', '.join(found_modules)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please specify which one to use with 'use module <module>' first.{Style.RESET_ALL}")
            return
        
        # Only one module has this tool, so use it
        module = found_modules[0]
        self.current_module = module
        self.current_script = script_name
        self.script_params = {}
        self.script_options = {}
        self.update_prompt()
        print(f"Selected tool: {Fore.GREEN}{script_name}{Style.RESET_ALL} from module {Fore.YELLOW}{module}{Style.RESET_ALL}")
        self.parse_tool_options()

    def parse_tool_options(self):
        """Parse the argparse options from the selected tool."""
        if not self.current_script:
            return
        
        script_path = os.path.join(SCRIPTS_DIR, self.current_module, f"{self.current_script}.py")
        self.script_options = {}
        
        # Try to load the module to extract argparse info
        try:
            # Read the file content
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Look for argparse patterns
            parser_pattern = r'(?:parser\s*=\s*argparse\.ArgumentParser\(.*?\))|(?:ArgumentParser\(.*?\))'
            parser_match = re.search(parser_pattern, content, re.DOTALL)
            
            if not parser_match:
                print(f"{Fore.YELLOW}No argument parser found in {self.current_script}.{Style.RESET_ALL}")
                return
            
            # Look for add_argument calls
            arg_pattern = r'(?:parser\.add_argument|add_argument)\(\s*[\'"](.*?)[\'"](.*?)\)'
            arg_matches = re.finditer(arg_pattern, content, re.DOTALL)
            
            for match in arg_matches:
                arg_name = match.group(1)
                arg_config = match.group(2)
                
                # Parse additional info from the arg_config
                help_match = re.search(r'help\s*=\s*[\'"](.+?)[\'"]', arg_config)
                help_text = help_match.group(1) if help_match else "No description"
                
                required_match = re.search(r'required\s*=\s*(True|False)', arg_config)
                required = required_match.group(1) == "True" if required_match else False
                
                default_match = re.search(r'default\s*=\s*[\'"]?(.+?)[\'"]?[,\)]', arg_config)
                default = default_match.group(1) if default_match else None
                
                # Clean up arg_name (remove leading dashes)
                clean_name = arg_name.lstrip('-')
                
                self.script_options[clean_name] = {
                    'original': arg_name,
                    'help': help_text,
                    'required': required,
                    'default': default
                }
                
                # Initialize empty parameter if required
                if required and clean_name not in self.script_params:
                    self.script_params[clean_name] = ""
        
        except Exception as e:
            print(f"{Fore.RED}Error parsing tool options: {e}{Style.RESET_ALL}")
    
    def do_show(self, args):
        """Show various information about the current context."""
        args = args.strip().lower()
        if args == "options":
            self.show_options()
        else:
            print(f"{Fore.RED}Invalid show command. Use 'show options'.{Style.RESET_ALL}")
    
    def show_options(self):
        """Show available options for the current tool."""
        if not self.current_script:
            print(f"{Fore.RED}No tool selected. Use 'use tool <tool_name>' first.{Style.RESET_ALL}")
            return
        
        if not self.script_options:
            print(f"{Fore.YELLOW}No options found for {self.current_script}.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Options for {Fore.GREEN}{self.current_script}{Fore.CYAN}:{Style.RESET_ALL}\n")
        
        # Display options in a formatted table
        # Define column widths
        col_widths = [12, 10, 30, 30, 50]
        
        # Print header
        print(f"{'Parameter':<{col_widths[0]}} {'Required':<{col_widths[1]}} {'Default':<{col_widths[2]}} {'Current Value':<{col_widths[3]}} {'Description'}")
        print(f"{'-' * col_widths[0]} {'-' * col_widths[1]} {'-' * col_widths[2]} {'-' * col_widths[3]} {'-' * col_widths[4]}")
        
        for name, details in self.script_options.items():
            # Format the required field
            required_field = f"{Fore.RED}yes{Style.RESET_ALL}" if details['required'] else "no"
            
            default = str(details['default'] if details['default'] is not None else "None")
            current = self.script_params.get(name, "")
            
            # Print with proper alignment, accounting for ANSI color code length when required is "yes"
            print(f"{name:<{col_widths[0]}} {required_field:<{col_widths[1] + (9 if details['required'] else 0)}} {default:<{col_widths[2]}} {current:<{col_widths[3]}} {details['help']}")
        
        print("\n")

    def do_set(self, args):
        """Set parameter value for the current tool."""
        if not self.current_script:
            print(f"{Fore.RED}No tool selected. Use 'use tool <tool_name>' first.{Style.RESET_ALL}")
            return
        
        parts = args.strip().split(maxsplit=1)
        if len(parts) != 2:
            print(f"{Fore.RED}Invalid command. Use 'set <parameter> <value>'.{Style.RESET_ALL}")
            return
        
        param, value = parts
        
        if param not in self.script_options:
            print(f"{Fore.RED}Parameter '{param}' not found in tool options.{Style.RESET_ALL}")
            return
        
        # Store the parameter value
        self.script_params[param] = value
        print(f"Set {Fore.GREEN}{param}{Style.RESET_ALL} => {Fore.YELLOW}{value}{Style.RESET_ALL}")
    
    def do_run(self, args):
        """Run the selected tool with current parameters."""
        if not self.current_script:
            print(f"{Fore.RED}No tool selected. Use 'use tool <tool_name>' first.{Style.RESET_ALL}")
            return
        
        # Check if all required parameters are set
        missing_params = []
        for param, details in self.script_options.items():
            if details['required'] and (param not in self.script_params or not self.script_params[param]):
                missing_params.append(param)
        
        if missing_params:
            print(f"{Fore.RED}Missing required parameters: {', '.join(missing_params)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Use 'set <parameter> <value>' to set required parameters.{Style.RESET_ALL}")
            return
        
        # Build the command to run the script
        script_path = os.path.join(SCRIPTS_DIR, self.current_module, f"{self.current_script}.py")
        
        # Build command with parameters
        cmd = [sys.executable, script_path]
        for param, value in self.script_params.items():
            if value:  # Only add parameters with values
                # Get the original parameter name (with dashes)
                original_param = self.script_options[param]['original']
                cmd.extend([original_param, value])
        
        print(f"\n{Fore.CYAN}Running tool: {Fore.GREEN}{self.current_script}{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Command: {' '.join(cmd)}{Style.RESET_ALL}\n")
        
        # Run the script
        try:
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            # Print stdout with green color
            if process.stdout:
                print(f"{Fore.GREEN}{process.stdout}{Style.RESET_ALL}")
            
            # Print stderr with red color
            if process.stderr:
                print(f"{Fore.RED}{process.stderr}{Style.RESET_ALL}")
            
            # Print return code
            exit_code = process.returncode
            if exit_code == 0:
                print(f"\n{Fore.GREEN}Tool completed successfully (exit code: {exit_code}){Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}Tool failed with exit code: {exit_code}{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}Error running tool: {e}{Style.RESET_ALL}")
        
        print("\n")

    def do_back(self, args):
        """Go back one level in the context."""
        if self.current_script:
            self.current_script = None
            self.script_params = {}
            self.script_options = {}
            self.update_prompt()
            print(f"Returned to module: {Fore.YELLOW}{self.current_module}{Style.RESET_ALL}")
        elif self.current_module:
            self.current_module = None
            self.update_prompt()
            print("Returned to main menu")
        else:
            print("Already at main menu")

    def do_exit(self, args):
        """Exit the program."""
        print(f"{Fore.GREEN}Exiting SecOps Toolkit. Goodbye!{Style.RESET_ALL}")
        return True

    def do_quit(self, args):
        """Exit the program."""
        return self.do_exit(args)

if __name__ == "__main__":
    loading_sequence()
    console = MyConsole()
    console.cmdloop()