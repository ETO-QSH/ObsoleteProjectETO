import main, inspect

def print_functions_and_params(module):
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        print(f"name: {name:36}", end='\t\t')
        signature = inspect.signature(obj)
        print("parameters: ", end='')
        for param_name, param in signature.parameters.items():
            print(f"{param}", end=' ')
        print()

print_functions_and_params(main)