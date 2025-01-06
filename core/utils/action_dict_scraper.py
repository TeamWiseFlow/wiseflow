from bs4 import BeautifulSoup

def action_dict_scraper(raw_html: str) -> dict:
    soup = BeautifulSoup(raw_html, 'html.parser')
    action_dict = {}
    # handle form elements
    for form in soup.find_all('form', recursive=True):
        form_dict = {}
        for input_elem in form.find_all('input'):
            input_type = input_elem.get('type', 'text')
            input_name = input_elem.get('name', f'input_{len(action_dict)}')
            input_value = ' '.join([f"{k}={v}" for k, v in input_elem.attrs.items() if k not in ['type', 'name', 'form']])
            input_dict = {
                "type": input_type,
                "values": [input_value] if input_value else []
            }

            # handle datalist
            if input_elem.get('list'):
                datalist = soup.find('datalist', id=input_elem['list'])
                if datalist:
                    options = [opt.get('value', opt.text.strip()) for opt in datalist.find_all('option')]
                    input_dict = {
                        "type": "text",
                        "values": [f"one of followings: {options}"]
                    }
                
            form_dict[input_name] = input_dict
            
        for select in form.find_all('select'):
            select_name = select.get('name', f'select_{len(form_dict)}')
            options = [opt.get('value', opt.text.strip()) for opt in select.find_all('option')]
            form_dict[select_name] = {
                "type": "select",
                "values": options
            }
                
        for textarea in form.find_all('textarea'):
            textarea_name = textarea.get('name', f'textarea_{len(form_dict)}')
            form_dict[textarea_name] = {
                "type": "textarea", 
                "values": [textarea.text.strip()]
            }
                
        if form_dict:
            form_id = form.get('id', f'form_{len(action_dict)}')
            action_dict[form_id] = form_dict
            
        form.decompose()
        
    # handle input elements that are not in any form
    for input_elem in soup.find_all('input', recursive=True):
        if input_elem.find_parent('form') is None:
            # check if the input is associated with a form by form attribute
            form_ids = input_elem.get('form', '').split()
                
            # handle input element
            input_type = input_elem.get('type', 'text')
            input_name = input_elem.get('name', f'input_{len(action_dict)}')
            input_value = ' '.join([f"{k}={v}" for k, v in input_elem.attrs.items() if k not in ['type', 'name', 'form']])
            input_dict = {
                "type": input_type,
                "values": [input_value] if input_value else []
            }

            # handle datalist
            if input_elem.get('list'):
                datalist = soup.find('datalist', id=input_elem['list'])
                if datalist:
                    options = [opt.get('value', opt.text.strip()) for opt in datalist.find_all('option')]
                    input_dict = {
                        "type": "text",
                        "values": [f"one of followings: {options}"]
                    }
                
            # decide the placement of the input element based on form attribute
            if form_ids:
                for form_id in form_ids:
                    if form_id in action_dict:
                        action_dict[form_id][input_name] = input_dict
                    else:
                        action_dict[form_id] = {input_name: input_dict}
            else:
                action_dict[input_name] = {"input": input_dict}

        input_elem.decompose()

    for button in soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]'], recursive=True):
        button_name = button.get('name', '') or button.get('id', '') or button.text.strip()
        if not button_name:
            button_name = f'button_{len(action_dict)}'
            
        button_type = button.get('type', 'button')
        button_value = button.get('value', button.text.strip())
            
        action_dict[button_name] = {
            "button": {
                "type": button_type,
                "values": [button_value] if button_value else []
            }
        }
            
        button.decompose()

    # handle command elements
    for command in soup.find_all('command', recursive=True):
        command_name = command.get('name', '') or command.get('id', '') or command.text.strip()
        if not command_name:
                command_name = f'command_{len(action_dict)}'
            
        command_type = command.get('type', 'command')
        command_value = command.get('value', command.text.strip())
            
        action_dict[command_name] = {
            "command": {
                "type": command_type,
                "values": [command_value] if command_value else []
            }
        }
            
        command.decompose()

    return action_dict
