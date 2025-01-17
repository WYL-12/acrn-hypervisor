# Copyright (C) 2019 Intel Corporation.
# SPDX-License-Identifier: BSD-3-Clause

"""View pages for config app.

"""

import os, copy
from datetime import datetime
from shutil import copyfile, move

# flask: Copyright 2010 Pallets
# SPDX-License-Identifier: BSD-3-Clause
# Refer to https://github.com/pallets/flask/blob/master/LICENSE.rst for the permission notice.
from flask import request, render_template, Blueprint, redirect, url_for, current_app

# werkzeug: Copyright 2007 Pallets
# SPDX-License-Identifier: BSD-3-Clause
# Refer to https://github.com/pallets/werkzeug/blob/master/LICENSE.rst for the permission notice.
from werkzeug.utils import secure_filename

import common
from controller import *
from scenario_config.scenario_cfg_gen import get_scenario_item_values
from scenario_config.scenario_cfg_gen import validate_scenario_setting
from launch_config.launch_cfg_gen import get_launch_item_values
from launch_config.launch_cfg_gen import validate_launch_setting
import scenario_config.default_populator as default_populator


CONFIG_APP = Blueprint('CONFIG_APP', __name__, template_folder='templates')


@CONFIG_APP.route('/')
def index():
    """
    render the index page
    :return: the render template of index page
    """
    return redirect(url_for('CONFIG_APP.scenarios'))


@CONFIG_APP.route('/scenario', methods=['GET'])
def scenarios():
    """
    render the scenario parent setting page
    :return: the render template of scenario setting parent page
    """
    board_info, board_type, scenario_config, launch_config = get_xml_configs()
    (bios_info, base_board_info) = get_board_info(board_info)
    scenario_list = ([], [])
    launch_list = ([], [])
    if board_type is not None:
        default_xml_config = XmlConfig(os.path.join(current_app.config.get('DEFAULT_CONFIG_PATH'), board_type))
        xml_config = XmlConfig(os.path.join(current_app.config.get('CONFIG_PATH'), board_type))
        generic_config_list = get_generic_config_list()
        if default_xml_config.list_all(xml_type='scenario')[0]:
            scenario_list = (
                default_xml_config.list_all(xml_type='scenario')[0], xml_config.list_all(xml_type='scenario')[0])
        else:
            scenario_list = (
                generic_config_list[0], xml_config.list_all(xml_type='scenario')[0])
        if default_xml_config.list_all(xml_type='user_vm_launcher')[0]:
            launch_list = (
                default_xml_config.list_all(xml_type='user_vm_launcher')[0],
                xml_config.list_all(xml_type='user_vm_launcher')[0])
        else:
            launch_list = (
                generic_config_list[1], xml_config.list_all(xml_type='user_vm_launcher')[0])

    return render_template('scenario.html', board_info_list=get_board_list(),
                           board_info=board_info, board_type=board_type,
                           bios_info=bios_info, base_board_info=base_board_info,
                           scenarios=scenario_list,
                           launches=launch_list,
                           scenario='', root=None)


@CONFIG_APP.route('/scenario/<scenario_name>', methods=['GET'])
def scenario(scenario_name):
    """
    render the specified scenario setting page
    :param scenario_name: the scenario type
    :return: the render template of the specified scenario setting page
    """

    board_info, board_type, scenario_config, launch_config = get_xml_configs()
    (bios_info, base_board_info) = get_board_info(board_info)
    scenario_list = ([], [])
    launch_list = ([], [])
    if board_type is not None:
        default_xml_config = XmlConfig(os.path.join(current_app.config.get('DEFAULT_CONFIG_PATH'), board_type))
        xml_config = XmlConfig(os.path.join(current_app.config.get('CONFIG_PATH'), board_type))
        generic_config_list = get_generic_config_list()
        if default_xml_config.list_all(xml_type='scenario')[0]:
            scenario_list = (
                default_xml_config.list_all(xml_type='scenario')[0], xml_config.list_all(xml_type='scenario')[0])
        else:
            scenario_list = (
                generic_config_list[0], xml_config.list_all(xml_type='scenario')[0])
        if default_xml_config.list_all(xml_type='user_vm_launcher')[0]:
            launch_list = (
                default_xml_config.list_all(xml_type='user_vm_launcher')[0],
                xml_config.list_all(xml_type='user_vm_launcher')[0])
        else:
            launch_list = (
                generic_config_list[1], xml_config.list_all(xml_type='user_vm_launcher')[0])

    xpath_dict = get_xpath_dict_of_xsd()

    current_app.config.update(SCENARIO=scenario_name)

    scenario_config.set_curr(scenario_name)

    scenario_item_values = {}
    if board_info is not None and board_type is not None:
        scenario_file_path = os.path.join(current_app.config.get('CONFIG_PATH'), board_type,
                                          scenario_name + '.xml')
        if os.path.isfile(scenario_file_path):
            scenario_item_values = get_scenario_item_values(
                os.path.join(current_app.config.get('CONFIG_PATH'), board_type, board_info+'.xml'),
                scenario_file_path)
    for xpath in xpath_dict:
        if xpath_dict[xpath]['enumeration'] and len(xpath.split('/')) > 2:
            scenario_item_values[','.join(xpath.split('/')[2:])] = xpath_dict[xpath]['enumeration']

    return render_template('scenario.html', board_info_list=get_board_list(),
                           board_info=board_info, board_type=board_type,
                           bios_info=bios_info, base_board_info=base_board_info,
                           scenarios=scenario_list,
                           launches=launch_list,
                           scenario=scenario_name, root=scenario_config.get_curr_root(),
                           scenario_item_values=scenario_item_values,
                           xpath_dict=xpath_dict)


@CONFIG_APP.route('/launch', methods=['GET'])
def launches():
    """
    render the parent launch setting page
    :return: the render template of launch setting page
    """
    board_info, board_type, scenario_config, launch_config = get_xml_configs()
    (bios_info, base_board_info) = get_board_info(board_info)
    scenario_list = ([], [])
    launch_list = ([], [])
    if board_type is not None:
        default_xml_config = XmlConfig(os.path.join(current_app.config.get('DEFAULT_CONFIG_PATH'), board_type))
        xml_config = XmlConfig(os.path.join(current_app.config.get('CONFIG_PATH'), board_type))
        generic_config_list = get_generic_config_list()
        if default_xml_config.list_all(xml_type='scenario')[0]:
            scenario_list = (
                default_xml_config.list_all(xml_type='scenario')[0], xml_config.list_all(xml_type='scenario')[0])
        else:
            scenario_list = (
                generic_config_list[0], xml_config.list_all(xml_type='scenario')[0])
        if default_xml_config.list_all(xml_type='user_vm_launcher')[0]:
            launch_list = (
                default_xml_config.list_all(xml_type='user_vm_launcher')[0],
                xml_config.list_all(xml_type='user_vm_launcher')[0])
        else:
            launch_list = (
                generic_config_list[1], xml_config.list_all(xml_type='user_vm_launcher')[0])

    return render_template('launch.html', board_info_list=get_board_list(),
                           board_info=board_info, board_type=board_type,
                           bios_info=bios_info, base_board_info=base_board_info,
                           scenarios=scenario_list,
                           launches=launch_list,
                           launch='', root=None)


@CONFIG_APP.route('/launch/<launch_name>', methods=['GET'])
def launch(launch_name):
    """
    render the specified launch setting page
    :param launch_name: the launch type
    :return: the render template of specified launch setting page
    """
    board_info, board_type, scenario_config, launch_config = get_xml_configs()
    (bios_info, base_board_info) = get_board_info(board_info)
    scenario_list = ([], [])
    launch_list = ([], [])
    if board_type is not None:
        default_xml_config = XmlConfig(os.path.join(current_app.config.get('DEFAULT_CONFIG_PATH'), board_type))
        xml_config = XmlConfig(os.path.join(current_app.config.get('CONFIG_PATH'), board_type))
        generic_config_list = get_generic_config_list()
        if default_xml_config.list_all(xml_type='scenario')[0]:
            scenario_list = (
                default_xml_config.list_all(xml_type='scenario')[0], xml_config.list_all(xml_type='scenario')[0])
        else:
            scenario_list = (
                generic_config_list[0], xml_config.list_all(xml_type='scenario')[0])
        if default_xml_config.list_all(xml_type='user_vm_launcher')[0]:
            launch_list = (
                default_xml_config.list_all(xml_type='user_vm_launcher')[0],
                xml_config.list_all(xml_type='user_vm_launcher')[0])
        else:
            launch_list = (
                generic_config_list[1], xml_config.list_all(xml_type='user_vm_launcher')[0])

    launch_config.set_curr(launch_name)

    launch_item_values = {}
    scenario_name = launch_config.get_curr_root().attrib['scenario']
    current_app.config.update(SCENARIO=scenario_name)
    scenario_name = current_app.config.get('SCENARIO')
    scenario_file = None
    if board_info is not None and scenario_name is not None:
        scenario_file = os.path.join(current_app.config.get('CONFIG_PATH'), board_type,
                                     scenario_name+'.xml')
        if not os.path.isfile(scenario_file):
            scenario_file = os.path.join(current_app.config.get('CONFIG_PATH'), board_type,
                                         scenario_name + '.xml')
            if not os.path.isfile(scenario_file):
                scenario_file = None
        launch_item_values = get_launch_item_values(
            os.path.join(current_app.config.get('CONFIG_PATH'), board_type, board_info + '.xml'), scenario_file)

    scenario_name = None
    launch_config_root = launch_config.get_curr_root()
    if launch_config_root is not None and 'scenario' in launch_config_root.attrib:
        scenario_name = launch_config_root.attrib['scenario']
    post_launch_vm_list = get_post_launch_vm_list(scenario_name)

    return render_template('launch.html', board_info_list=get_board_list(),
                           board_info=board_info, board_type=board_type,
                           bios_info=bios_info, base_board_info=base_board_info,
                           scenarios=scenario_list,
                           launches=launch_list,
                           launch=launch_name, root=launch_config.get_curr_root(),
                           scenario=current_app.config.get('SCENARIO'),
                           post_launch_vm_list=post_launch_vm_list,
                           launch_item_values=launch_item_values)


@CONFIG_APP.route('/save_scenario', methods=['POST'])
def save_scenario():
    """
    save scenario setting.
    :return: the error list for the edited scenario setting.
    """
    scenario_config_data = request.json if request.method == "POST" else request.args
    xml_configs = get_xml_configs()
    board_type = xml_configs[1]
    scenario_config = xml_configs[3]

    common.MAX_VM_NUM = int(scenario_config_data['hv,CAPACITIES,MAX_VM_NUM'])
    if board_type is None or xml_configs[0] is None:
        return {'status': 'fail',
                'error_list': {'error': 'Please select the board info before this operation.'}}

    scenario_path = os.path.join(current_app.config.get('CONFIG_PATH'), board_type)
    old_scenario_name = scenario_config_data['old_scenario_name']
    scenario_config.set_curr(old_scenario_name)

    for vm in list(scenario_config.get_curr_root()):
        if vm.tag == 'vm':
            for elem in list(vm):
                if elem.tag in ['communication_vuart', 'console_vuart']:
                    vuart_key = vm.tag+':id='+vm.attrib['id']+','+elem.tag + ':id='+elem.attrib['id']
                    delete_flag = True
                    for key in scenario_config_data:
                        if key.find(vuart_key) >= 0:
                            delete_flag = False
                            break
                    if delete_flag:
                        scenario_config.delete_curr_elem(*tuple(vuart_key.split(',')))

    for key in scenario_config_data:
        if scenario_config_data[key] in [None, 'None']:
            scenario_config_data[key] = ''

        if key not in ['old_scenario_name', 'new_scenario_name', 'generator', 'add_vm_type', 'src_path']:
            if isinstance(scenario_config_data[key], list):
                scenario_config.set_curr_list(scenario_config_data[key], *tuple(key.split(',')))
            elif key.find('communication_vuart') >= 0:
                try:
                    scenario_config.get_curr_elem(*tuple(key.split(',')))
                except:
                    communication_vuart_id = key.split(',')[1].split('=')[1].strip()
                    communication_vuart_1_item = scenario_config.get_curr_elem(
                        *tuple([key.split(',')[0], 'communication_vuart:id=1']))
                    communication_vuart_i_item = copy.deepcopy(communication_vuart_1_item)
                    communication_vuart_i_item.attrib['id'] = communication_vuart_id
                    curr_index = 0
                    elem_list = list(scenario_config.get_curr_elem(key.split(',')[0]))
                    for elem in reversed(elem_list):
                        curr_index += 1
                        if elem.tag in ['communication_vuart', 'console_vuart']:
                            break
                    scenario_config.insert_curr_elem(len(elem_list)-curr_index+1, communication_vuart_i_item, key.split(',')[0])
                finally:
                    scenario_config.set_curr_value(scenario_config_data[key], *tuple(key.split(',')))
            else:
                scenario_config.set_curr_value(scenario_config_data[key], *tuple(key.split(',')))

            # how to put added vuart under vuart!!!
            # delete vuart without key!!!

    generator = scenario_config_data['generator']
    if generator is not None:
        if generator.startswith('add_vm:'):
            vm_list = []
            for vm in list(scenario_config.get_curr_root()):
                if vm.tag == 'vm':
                    vm_list.append(vm.attrib['id'])
            if len(vm_list) >= common.MAX_VM_NUM:
                return {'status': 'fail',
                        'error_list': {'error': 'Cannot add a new VM. hv.CAPACITIES.MAX_VM_NUM is currently set to {}.'.format(common.MAX_VM_NUM)}}
            curr_vm_id = generator.split(':')[1]
            add_vm_type = scenario_config_data['add_vm_type']
            add_scenario_config = get_generic_scenario_config(scenario_config, add_vm_type)
            vm_to_add = []
            if str(curr_vm_id) == '-1':
                curr_vm_index = 1
            else:
                curr_vm_index = len(vm_list) + 1
                for i in range(len(vm_list)):
                    if curr_vm_id == vm_list[i]:
                        curr_vm_index = i + 2
                        break
            if add_scenario_config is not None and add_scenario_config.tag == 'vm':
                for i in range(0, common.MAX_VM_NUM):
                    if str(i) not in vm_list:
                        break
                add_scenario_config.attrib['id'] = str(i)
                vm_to_add.append(add_scenario_config)
            for vm in vm_to_add:
                scenario_config.insert_curr_elem(curr_vm_index, vm)
                curr_vm_index += 1
            assign_vm_id(scenario_config)
        elif generator.startswith('remove_vm:'):
            remove_vm_id = generator.split(':')[1]
            scenario_config.delete_curr_key('vm:id='+remove_vm_id.strip())
            assign_vm_id(scenario_config)

    scenario_config.set_curr_attr('board', board_type)
    scenario_config.set_curr_attr('scenario', scenario_config_data['new_scenario_name'])

    tmp_scenario_file = os.path.join(scenario_path,
                                     'tmp_'+scenario_config_data['new_scenario_name']+'.xml')

    scenario_config.save('tmp_'+scenario_config_data['new_scenario_name'])

    # call validate function
    error_list = {}
    new_scenario_name = scenario_config_data['new_scenario_name']
    rename = False
    try:
        if generator is None or not (generator.startswith('add_vm:') or generator.startswith('remove_vm:')):
            (error_list, vm_info) = validate_scenario_setting(
                os.path.join(current_app.config.get('CONFIG_PATH'), board_type, xml_configs[0]+'.xml'),
                tmp_scenario_file)
    except Exception as error:
        if os.path.isfile(tmp_scenario_file):
            os.remove(tmp_scenario_file)
        return {'status': 'fail', 'file_name': new_scenario_name,
                'rename': rename, 'error_list': {'error': str(error)}}

    if not error_list:
        scenario_config.save(new_scenario_name)

    if os.path.isfile(tmp_scenario_file):
        os.remove(tmp_scenario_file)

    src_path = scenario_config_data['src_path']
    if src_path is not None and str(src_path).strip() != '':
        if not os.path.isdir(src_path):
            os.makedirs(src_path)
        copyfile(os.path.join(scenario_path, scenario_config_data['new_scenario_name']+'.xml'),
                 os.path.join(src_path, scenario_config_data['new_scenario_name']+'.xml'))

    return {'status': 'success', 'file_name': new_scenario_name,
            'rename': rename, 'error_list': error_list}


@CONFIG_APP.route('/save_launch', methods=['POST'])
def save_launch():
    """
    save launch setting.
    :return: the error list of the edited launch setting.
    """
    launch_config_data = request.json if request.method == "POST" else request.args
    xml_configs = get_xml_configs()
    launch_config = xml_configs[3]

    if xml_configs[1] is None or xml_configs[0] is None:
        return {'status': 'fail',
                'error_list': {'error': 'Please select the board info before this operation.'}}

    old_launch_name = launch_config_data['old_launch_name']
    launch_config.set_curr(old_launch_name)
    scenario_name = launch_config_data['scenario_name']
    scenario_file_path = os.path.join(current_app.config.get('CONFIG_PATH'),
                                      current_app.config.get('BOARD_TYPE'),
                                      scenario_name + '.xml')
    # update VM_COUNT and MAX_VM_NUM
    common.get_vm_num(scenario_file_path)

    for key in launch_config_data:
        if launch_config_data[key] in [None, 'None']:
            launch_config_data[key] = ''
        if key not in ['old_launch_name', 'new_launch_name', 'generator', 'add_launch_type', 'scenario_name', 'src_path']:
            if isinstance(launch_config_data[key], list):
                launch_config.set_curr_list(launch_config_data[key], *tuple(key.split(',')))
            else:
                launch_config.set_curr_value(launch_config_data[key], *tuple(key.split(',')))

    generator = launch_config_data['generator']
    if generator is not None:
        if generator.startswith('add_vm:'):
            vm_list = []
            for vm in list(launch_config.get_curr_root()):
                if vm.tag == 'user_vm':
                    vm_list.append(vm.attrib['id'])
            if len(vm_list) >= common.MAX_VM_NUM:
                return {
                    'status': 'fail',
                    'error_list': {
                        'error': 'Cannot add a new VM. hv.CAPACITIES.MAX_VM_NUM '
                                 'is currently set to {}.'.format(common.MAX_VM_NUM)
                    }
                }
            curr_vm_id = generator.split(':')[1].strip()
            add_launch_type = launch_config_data['add_launch_type']
            if add_launch_type is None or len(add_launch_type.split('ID :')) < 2:
                return {'status': 'fail',
                        'error_list': {'error': 'No VM is selected. '
                                                'Please select a scenario with available post launched VMs.'}}
            add_vm_id = add_launch_type.split('ID :')[1].replace(')', '').strip()
            add_launch_type = 'LAUNCH_' + add_launch_type.split()[0]
            add_launch_id = 1
            post_vm_list = get_post_launch_vm_list(scenario_name)
            for i in range(len(post_vm_list)):
                vm_info = post_vm_list[i]
                if add_vm_id == vm_info[0]:
                    add_launch_id = i + 1
                    break
            add_launch_config = get_generic_scenario_config(launch_config, add_launch_type)
            vm_to_add = []
            if str(curr_vm_id) == '-1':
                curr_vm_index = len(vm_list)
            else:
                curr_vm_index = 0
                for i in range(len(vm_list)):
                    if curr_vm_id == vm_list[i]:
                        curr_vm_index = i + 1
                        break
            if add_launch_config is not None and add_launch_config.tag == 'user_vm':
                for i in range(1, common.MAX_VM_NUM):
                    if str(i) not in vm_list:
                        break
                add_launch_config.attrib['id'] = str(add_launch_id)
                vm_to_add.append(add_launch_config)

            for vm in vm_to_add:
                launch_config.insert_curr_elem(curr_vm_index, vm)
        elif generator.startswith('remove_vm:'):
            remove_vm_id = generator.split(':')[1]
            launch_config.delete_curr_key('user_vm:id='+remove_vm_id.strip())

    launch_config.set_curr_attr('scenario', scenario_name)
    launch_config.set_curr_attr('board', current_app.config.get('BOARD_TYPE'))

    launch_config.set_curr_attr('user_vm_launcher', str(len(list(launch_config.get_curr_root()))))

    tmp_launch_file = os.path.join(current_app.config.get('CONFIG_PATH'), xml_configs[1],
                                   'tmp_' + launch_config_data['new_launch_name'] + '.xml')

    launch_config.save('tmp_' + launch_config_data['new_launch_name'])

    # call validate function
    error_list = {}
    rename = False
    try:
        if generator is None or not (generator.startswith('add_vm:') or generator.startswith('remove_vm:')):
            (error_list, pthru_sel, virtio, dm_value, sriov) = validate_launch_setting(
                os.path.join(current_app.config.get('CONFIG_PATH'), xml_configs[1], xml_configs[0]+'.xml'),
                scenario_file_path,
                tmp_launch_file)
    except Exception as error:
        if os.path.isfile(tmp_launch_file):
            os.remove(tmp_launch_file)
        return {'status': 'fail', 'file_name': launch_config_data['new_launch_name'],
                'rename': rename, 'error_list': {'launch config error': str(error)}}

    if not error_list:
        launch_config.save(launch_config_data['new_launch_name'])

    if os.path.isfile(tmp_launch_file):
        os.remove(tmp_launch_file)

    src_path = launch_config_data['src_path']
    if src_path is not None and str(src_path).strip() != '':
        if not os.path.isdir(src_path):
            os.makedirs(src_path)
        copyfile(os.path.join(current_app.config.get('CONFIG_PATH'), current_app.config.get('BOARD_TYPE'),
                              launch_config_data['new_launch_name'] + '.xml'),
                 os.path.join(src_path, launch_config_data['new_launch_name'] + '.xml'))

    return {'status': 'success', 'file_name': launch_config_data['new_launch_name'],
            'rename': rename, 'error_list': error_list}


@CONFIG_APP.route('/check_setting_exist', methods=['POST'])
def check_setting_exist():
    """
    check the setting exist or not.
    :return: setting exist or not.
    """
    config_data = request.json if request.method == "POST" else request.args
    src_path = config_data['src_path']

    board_info = current_app.config.get('BOARD_TYPE')
    setting_path = os.path.join(current_app.config.get('CONFIG_PATH'), board_info)
    if src_path is not None and str(src_path).strip() != '':
        setting_path = src_path

    if 'old_scenario_name' in list(config_data.keys()) and 'new_scenario_name' in list(config_data.keys()):
        if config_data['old_scenario_name'] != config_data['new_scenario_name'] and \
           os.path.isfile(os.path.join(setting_path, config_data['new_scenario_name'] + '.xml')):
            return {'exist': 'yes'}
        else:
            return {'exist': 'no'}
    elif 'old_launch_name' in list(config_data.keys()) and 'new_launch_name' in list(config_data.keys()):
        if config_data['old_launch_name'] != config_data['new_launch_name'] and \
           os.path.isfile(os.path.join(setting_path, config_data['new_launch_name'] + '.xml')):
            return {'exist': 'yes'}
        else:
            return {'exist': 'no'}
    elif 'create_name' in list(config_data.keys()):
        if os.path.isfile(os.path.join(setting_path, config_data['create_name'] + '.xml')):
            return {'exist': 'yes'}
        else:
            return {'exist': 'no'}
    else:
        return {'exist': 'no'}


@CONFIG_APP.route('/create_setting', methods=['POST'])
def create_setting():
    """
    create a new scenario or launch setting.
    :return: the status and error list of the created scenario or launch setting.
    """
    create_config_data = request.json if request.method == "POST" else request.args
    mode = create_config_data['mode']
    default_name = create_config_data['default_name']
    create_name = create_config_data['create_name']
    src_path = create_config_data['src_path']
    setting_type = create_config_data['type']

    xml_configs = get_xml_configs()
    board_info = xml_configs[0]
    board_type = xml_configs[1]
    scenario_config = xml_configs[2]
    launch_config = xml_configs[3]

    if board_type is None or xml_configs[0] is None:
        return {'status': 'fail',
                'error_list': {'error': 'Please select the board info before this operation.'}}

    setting_path = os.path.join(current_app.config.get('CONFIG_PATH'), board_info)
    if not os.path.isdir(setting_path):
        os.makedirs(setting_path)

    if src_path is not None and str(src_path).strip() != '':
        setting_path = src_path
    if not os.path.isdir(setting_path):
        os.makedirs(setting_path)

    if create_config_data['type'] == 'launch':
        launch_file = os.path.join(setting_path,  create_name + '.xml')

        if mode == 'create':
            template_file_name = 'hybrid_launch_2user_vm'
            src_file_name = os.path.join(current_app.config.get('DEFAULT_CONFIG_PATH'), 'generic_board', template_file_name + '.xml')
        else: #load
            src_file_name = os.path.join(current_app.config.get('DEFAULT_CONFIG_PATH'), board_type, default_name + '.xml')
        if os.path.isfile(src_file_name):
            if os.path.isfile(launch_file):
                os.remove(launch_file)
            copyfile(src_file_name,
                     os.path.join(current_app.config.get('CONFIG_PATH'), board_type, create_name + '.xml'))

        launch_config.set_curr(create_name)
        if mode == 'create':
            launch_config.delete_curr_key('user_vm:id=2')
            launch_config.delete_curr_key('user_vm:id=1')
        launch_config.save(create_name)
        if os.path.normcase(setting_path) != os.path.normcase(os.path.join(current_app.config.get('CONFIG_PATH'), board_type)):
            copyfile(os.path.join(current_app.config.get('CONFIG_PATH'), board_type, create_name + '.xml'),
                 os.path.join(setting_path, create_name + '.xml'))
        return {'status': 'success', 'setting': create_name, 'error_list': {}}

    elif create_config_data['type'] == 'scenario':
        scenario_file = os.path.join(setting_path, create_name + '.xml')

        if mode == 'create':
            template_file_name = 'shared'
            src_file_name = os.path.join(current_app.config.get('DEFAULT_CONFIG_PATH'), 'generic_board', template_file_name + '.xml')
        else: # load
            src_file_name = os.path.join(current_app.config.get('DEFAULT_CONFIG_PATH'), board_type,
                                         default_name + '.xml')
            if not os.path.isfile(src_file_name):
                src_file_name=os.path.join(current_app.config.get('DEFAULT_CONFIG_PATH'), 'generic_board', default_name + '.xml')

        if os.path.isfile(src_file_name):
            xsd_path =  os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'schema', 'config.xsd')
            out_xml = os.path.join(os.path.dirname(os.path.abspath(__file__)), create_name + '.xml')
            default_populator.main(xsd_path, src_file_name, out_xml)
            if os.path.isfile(scenario_file):
                os.remove(scenario_file)
            copyfile(out_xml,
                 os.path.join(current_app.config.get('CONFIG_PATH'), board_type,
                              create_name + '.xml'))
            os.remove(out_xml)

        if mode == 'create':
            # update RDT->CLOS_MASK according to board xml
            scenario_config.set_curr(create_name)
            elem_clos_max = scenario_config.get_curr_elem('hv', 'FEATURES', 'RDT', 'CLOS_MASK')
            # elem_mba_delay = scenario_config.get_curr_elem('hv', 'FEATURES', 'RDT', 'MBA_DELAY')
            scenario_config.delete_curr_elem('hv', 'FEATURES', 'RDT', 'CLOS_MASK')
            # scenario_config.delete_curr_elem('hv', 'FEATURES', 'RDT', 'MBA_DELAY')
            cdp_enabled = scenario_config.get_curr_value('hv', 'FEATURES', 'RDT', 'CDP_ENABLED')
            (num_clos_mask, num_mba_delay) = get_num_of_rdt_res(board_info, cdp_enabled)
            for i in range(num_clos_mask):
                scenario_config.clone_curr_elem(elem_clos_max, 'hv', 'FEATURES', 'RDT')
            # for i in range(num_mba_delay):
            #    scenario_config.clone_curr_elem(elem_mba_delay, 'hv', 'FEATURES', 'RDT')
            for i in range(7):
                scenario_config.delete_curr_key('vm:id={}'.format(i))
            scenario_config = set_default_config(scenario_config)
        scenario_config.save(create_name)
        if os.path.normcase(setting_path) != os.path.normcase(os.path.join(current_app.config.get('CONFIG_PATH'), board_type)):
            copyfile(os.path.join(current_app.config.get('CONFIG_PATH'), board_type, create_name + '.xml'),
                     os.path.join(setting_path, create_name + '.xml'))
        return {'status': 'success', 'setting': create_name, 'error_list': {}}

    else:
        return {'status': 'fail', 'error_list': {'name': 'Unsupported setting type. '}}


@CONFIG_APP.route('/remove_setting', methods=['POST'])
def remove_setting():
    """
    remove current setting from config app
    :return: the return message
    """
    remove_config_data = request.json if request.method == "POST" else request.args

    old_setting_name = remove_config_data['old_setting_name']

    if current_app.config.get('BOARD_TYPE') is None:
        return {'status': 'Board info not set before remove current setting'}

    old_setting_path = os.path.join(current_app.config.get('CONFIG_PATH'),
                                    current_app.config.get('BOARD_TYPE'),
                                    old_setting_name + '.xml')

    if os.path.isfile(old_setting_path):
        os.remove(old_setting_path)
    return {'status': 'success'}


@CONFIG_APP.route('/generate_src', methods=['POST'])
def generate_src():
    """
    generate board src or scenario src
    :return: the error message
    """
    generator_config_data = request.json if request.method == "POST" else request.args

    src_type = generator_config_data['type']
    board_info = generator_config_data['board_info']
    board_type = current_app.config.get('BOARD_TYPE')
    board_info_xml = os.path.join(current_app.config.get('CONFIG_PATH'),
                                  board_type, board_info+'.xml')
    scenario_setting = generator_config_data['scenario_setting']
    scenario_setting_xml = os.path.join(current_app.config.get('CONFIG_PATH'), board_type,
                                        scenario_setting+'.xml')
    src_path = generator_config_data['src_path']
    if src_path is None or str(src_path).strip() == '':
        src_path = os.path.join(current_app.config.get('CONFIG_PATH'))
    launch_setting_xml = None
    if 'launch_setting' in generator_config_data:
        launch_setting = generator_config_data['launch_setting']
        launch_setting_xml = os.path.join(current_app.config.get('CONFIG_PATH'),
                                          board_type, launch_setting + '.xml')
    msg = {}
    error_list = {}
    status = 'success'
    if src_type == 'generate_config_src':
        try:
            from board_config.board_cfg_gen import ui_entry_api
            error_list = ui_entry_api(board_info_xml, scenario_setting_xml, src_path)
        except Exception as error:
            status = 'fail'
            error_list = {'board setting error': str(error)}

        try:
            from scenario_config.scenario_cfg_gen import ui_entry_api
            error_list = ui_entry_api(board_info_xml, scenario_setting_xml, src_path)
        except Exception as error:
            status = 'fail'
            error_list = {'scenario setting error': str(error)}
    elif src_type == 'generate_launch_script':
        scenario_setting_xml = os.path.join(current_app.config.get('CONFIG_PATH'), board_type,
                                            scenario_setting + '.xml')

        try:
            from launch_config.launch_cfg_gen import ui_entry_api
            error_list = ui_entry_api(board_info_xml, scenario_setting_xml, launch_setting_xml, src_path)
        except Exception as error:
            status = 'fail'
            error_list = {'launch setting error': str(error)}
    else:
        status = 'fail'
        error_list = {'error': 'generator type not specified'}

    msg = {'status': status, 'error_list': error_list}
    return msg


@CONFIG_APP.route('/upload_board_info', methods=['POST'])
def upload_board_info():
    """
    upload board info xml file
    :return: the upload status
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            return {'status': 'Error: no file uploaded'}
        file = request.files['file']
        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1] in ['xml']:
            filename = secure_filename(file.filename)
            tmp_filename = 'tmp_' + filename
            config_path = current_app.config.get('CONFIG_PATH')
            default_config_path = current_app.config.get('DEFAULT_CONFIG_PATH')
            save_tmp_board_path = os.path.join(config_path, tmp_filename)
            file.save(save_tmp_board_path)

            board_type_list = []
            for config_name in os.listdir(default_config_path):
                if os.path.isdir(os.path.join(default_config_path, config_name)) \
                        and config_name not in ['generic_board', 'sample_launch_scripts']:
                    board_type_list.append(config_name)

            board_info_config = XmlConfig(config_path)
            board_info_config.set_curr(tmp_filename.rsplit('.', 1)[0])
            board_info_root = board_info_config.get_curr_root()
            board_type = None
            if board_info_root is not None and 'board' in board_info_root.attrib \
                and 'scenario' not in board_info_root.attrib \
                    and 'user_vm_launcher' not in board_info_root.attrib:
                board_type = board_info_root.attrib['board']
            if not board_type:
                os.remove(save_tmp_board_path)
                return {'status': 'Error on parsing Board info\n'
                                  'check the xml syntax and whether there is only the board '
                                  'attribute in the board info file'}

            board_path =os.path.join(config_path, board_type)
            if not os.path.isdir(board_path):
                os.makedirs(board_path)
            move(save_tmp_board_path, os.path.join(board_path, filename))
            info = 'updated'
            if board_type not in board_type_list:
                info = board_type
                for generic_name in os.listdir(os.path.join(default_config_path, 'generic_board')):
                    generic_file = os.path.join(default_config_path, 'generic_board', generic_name)
                    if os.path.isfile(generic_file):
                        new_file = os.path.join(board_path, generic_name)
                        copyfile(generic_file, new_file)
                        xml_config = XmlConfig(board_path)
                        xml_config.set_curr(generic_name.rsplit('.', 1)[0])
                        xml_config.set_curr_attr('board', board_type)
                        xml_config_root = xml_config.get_curr_root()
                        if 'scenario' not in xml_config_root.attrib and 'user_vm_launcher' not in xml_config_root.attrib:
                            os.remove(new_file)
                            continue
                        # update RDT->CLOS_MASK according to board xml
                       # if 'board' in xml_config_root.attrib and 'scenario' in xml_config_root.attrib \
                           #     and 'uos_launcher' not in xml_config_root.attrib:
                           # cdp_enabled = xml_config.get_curr_value('hv', 'FEATURES', 'RDT', 'CDP_ENABLED')
                           # (num_clos_mask, num_mba_delay) = \
                           #     get_num_of_rdt_res(filename.rsplit('.', 1)[0], cdp_enabled)
                           # elem_clos_max = xml_config.get_curr_elem('hv', 'FEATURES', 'RDT', 'CLOS_MASK')
                           # elem_mba_delay = xml_config.get_curr_elem('hv', 'FEATURES', 'RDT', 'MBA_DELAY')
                           # xml_config.delete_curr_elem('hv', 'FEATURES', 'RDT', 'CLOS_MASK')
                           # xml_config.delete_curr_elem('hv', 'FEATURES', 'RDT', 'MBA_DELAY')
                           # for i in range(num_clos_mask):
                           #     xml_config.clone_curr_elem(elem_clos_max, 'hv', 'FEATURES', 'RDT')
                           # for i in range(num_mba_delay):
                           #     xml_config.clone_curr_elem(elem_mba_delay, 'hv', 'FEATURES', 'RDT')
                            # xml_config = set_default_config(xml_config)
                        xml_config.save(generic_name.rsplit('.', 1)[0], user_defined=False)

            board_info = os.path.splitext(file.filename)[0]
            current_app.config.update(BOARD_INFO=board_info)
            current_app.config.update(BOARD_TYPE=board_type)

            return {'status': 'success', 'info': info}

    return {'status': 'Error: upload failed'}


@CONFIG_APP.route('/select_board', methods=['POST'])
def select_board():
    """
    select one board info
    :return: the selected board info
    """
    data = request.json if request.method == "POST" else request.args
    board_info = data['board_info']
    current_app.config.update(BOARD_INFO=board_info)

    board_type = get_board_type(board_info)
    current_app.config.update(BOARD_TYPE=board_type)
    if board_type:
        return board_type

    return ''


@CONFIG_APP.route('/upload_scenario', methods=['POST'])
def upload_scenario():
    """
    upload scenario setting xml file
    :return: the upload status
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            return {'status': 'no file uploaded'}
        file = request.files['file']
        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1] in ['xml']:
            filename = secure_filename(file.filename)
            scenario_file_name = os.path.splitext(file.filename)[0]
            board_type = current_app.config.get('BOARD_TYPE')

            tmp_scenario_name = 'tmp_' + scenario_file_name + '.xml'
            tmp_scenario_file = os.path.join(current_app.config.get('CONFIG_PATH'), board_type, tmp_scenario_name)
            tmp_scenario_folder = os.path.dirname(tmp_scenario_file)
            if not os.path.exists(tmp_scenario_folder):
                os.makedirs(tmp_scenario_folder)
            if os.path.isfile(tmp_scenario_file):
                os.remove(tmp_scenario_file)

            file.save(tmp_scenario_file)

            tmp_xml_config = XmlConfig(os.path.join(current_app.config.get('CONFIG_PATH'),
                                                    board_type))
            tmp_xml_config.set_curr(tmp_scenario_name[:-4])
            status = None
            if tmp_xml_config.get_curr_root() is None:
                status = 'Error on parsing the scenario xml file, \n' \
                         'check the xml syntax and config items.'
            else:
                tmp_root = tmp_xml_config.get_curr_root()
                if 'board' not in tmp_root.attrib or 'scenario' not in tmp_root.attrib \
                        or 'user_vm_launcher' in tmp_root.attrib:
                    status = 'Invalid scenario xml file, \nonly board and scenario ' \
                             'need to be configured.'
                elif tmp_root.attrib['board'] != current_app.config.get('BOARD_TYPE'):
                    status = 'Current board: {} mismatched with the board in the scenario file,' \
                             '\nplease reselect or upload the board info: {}'\
                        .format(current_app.config.get('BOARD_TYPE'), tmp_root.attrib['board'])
            if status is not None:
                if os.path.isfile(tmp_scenario_file):
                    os.remove(tmp_scenario_file)
                return {'status': status}

            error_list = {}
            new_scenario_name = scenario_file_name
            rename = False
            if not error_list:
                new_scenario_path = os.path.join(current_app.config.get('CONFIG_PATH'), board_type,
                                                 scenario_file_name + '.xml')
                if os.path.isfile(new_scenario_path):
                    new_scenario_name = new_scenario_name + '_' \
                                        + datetime.now().strftime('%Y%m%d%H%M%S')
                    rename = True

            xsd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'schema', 'config.xsd')
            default_populator.main(xsd_path, tmp_scenario_file, tmp_scenario_file)
            os.rename(tmp_scenario_file, os.path.join(current_app.config.get('CONFIG_PATH'),
                                                      board_type, new_scenario_name + '.xml'))

            return {'status': 'success', 'file_name': new_scenario_name,
                    'rename': rename, 'error_list': error_list}

    return {'status': 'unsupported method'}


@CONFIG_APP.route('/upload_launch', methods=['POST'])
def upload_launch():
    """
    upload scenario setting xml file
    :return: the upload status
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            return {'status': 'no file uploaded'}
        file = request.files['file']
        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1] in ['xml']:
            filename = secure_filename(file.filename)
            launch_file_name = os.path.splitext(file.filename)[0]
            board_type = current_app.config.get('BOARD_TYPE')

            tmp_launch_name = 'tmp_' + launch_file_name + '.xml'
            tmp_launch_file = os.path.join(current_app.config.get('CONFIG_PATH'), board_type,
                                           tmp_launch_name)
            if os.path.isfile(tmp_launch_file):
                os.remove(tmp_launch_file)

            file.save(tmp_launch_file)

            tmp_xml_config = XmlConfig(os.path.join(current_app.config.get('CONFIG_PATH'),
                                                    board_type))
            tmp_xml_config.set_curr(tmp_launch_name[:-4])
            status = None
            if tmp_xml_config.get_curr_root() is None:
                status = 'Error on parsing the scenario xml file, \n' \
                         'check the xml syntax and config items.'
            else:
                tmp_root = tmp_xml_config.get_curr_root()
                if 'board' not in tmp_root.attrib or 'scenario' not in tmp_root.attrib \
                        or 'user_vm_launcher' not in tmp_root.attrib:
                    status = 'Invalid launch xml file, \nboard, scenario,' \
                             'and user_vm_launcher need to be configured.'
                elif tmp_root.attrib['board'] != current_app.config.get('BOARD_TYPE'):
                    status = 'Current board: {} mismatched with the board in the launch file,' \
                             '\nplease reselect or upload the board info: {}' \
                        .format(current_app.config.get('BOARD_TYPE'), tmp_root.attrib['board'])
            if status is not None:
                if os.path.isfile(tmp_launch_file):
                    os.remove(tmp_launch_file)
                return {'status': status}

            error_list = {}
            new_launch_name = launch_file_name
            rename = False
            if not error_list:
                new_launch_path = os.path.join(current_app.config.get('CONFIG_PATH'), board_type,
                                               launch_file_name + '.xml')
                if os.path.isfile(new_launch_path):
                    new_launch_name = new_launch_name + '_' + \
                                      datetime.now().strftime('%Y%m%d%H%M%S')
                    rename = True

            os.rename(tmp_launch_file, os.path.join(current_app.config.get('CONFIG_PATH'),
                                                    board_type, new_launch_name + '.xml'))

            return {'status': 'success', 'file_name': new_launch_name,
                    'rename': rename, 'error_list': error_list}

    return {'status': 'unsupported method'}


@CONFIG_APP.route('/get_post_launch_vms', methods=['POST'])
def get_post_launch_vms():
    """
    get vm list for the scenario setting
    :return: the vm list
    """
    data = request.json if request.method == "POST" else request.args
    scenario_name = data['scenario_name']
    current_app.config.update(SCENARIO=scenario_name)

    vm_list = get_post_launch_vm_list(scenario_name)

    user_vmid_list = []
    launch_name = data['launch_name']
    xml_configs = get_xml_configs()
    launch_config = xml_configs[3]
    launch_config.set_curr(launch_name)
    if launch_config is not None and launch_config.get_curr_root() is not None:
        for user_vm in list(launch_config.get_curr_root()):
            if 'id' in user_vm.attrib:
                user_vmid_list.append(int(user_vm.attrib['id'])-1)

    vm_list_index = [i for i in range(len(vm_list))]
    vm_list_index = set(vm_list_index)
    user_vmid_list = set(user_vmid_list)
    index = list(vm_list_index - user_vmid_list)
    vm_list = [vm_list[i] for i in index]

    return {'vm_list': vm_list}


@CONFIG_APP.route('/get_num_of_rdt_res_entries', methods=['POST'])
def get_num_of_rdt_res_entries():
    """
    get the number of rdt res entries
    :return: the number of CLOS_MASK and MBA_DELAY entries
    """
    data = request.json if request.method == "POST" else request.args
    cdp_enabled = data['cdp_enabled']
    board_info = current_app.config.get('BOARD_INFO')
    (num_clos_mask, num_mba_delay) = get_num_of_rdt_res(board_info, cdp_enabled)
    return {'num_clos_mask': num_clos_mask, 'num_mba_delay': num_mba_delay}


def get_post_launch_vm_list(scenario_name):
    """
    get post launch VM list
    :param scenario_name:
    :return: vm_list
    """
    xml_configs = get_xml_configs()
    scenario_config = xml_configs[3]
    scenario_config.set_curr(scenario_name)
    vm_list = []
    if scenario_config is not None and scenario_config.get_curr_root() is not None:
        for vm in list(scenario_config.get_curr_root()):
            if vm.tag == 'vm' and 'id' in vm.attrib:
                vm_id = vm.attrib['id']
                for item in list(vm):
                    if item.tag == 'vm_type' and item.text in ['POST_STD_VM', 'POST_RT_VM']:
                        vm_list.append((vm_id, item.text))
                        break
    return vm_list


def get_board_list():
    """
    get all available board info files
    :return: the file list of board info
    """
    config_path = current_app.config.get('CONFIG_PATH')
    board_type_list = []
    for config_name in os.listdir(config_path):
        if os.path.isdir(os.path.join(config_path, config_name)) \
                and config_name not in ['generic_board', 'sample_launch_scripts']:
            board_type_list.append(config_name)

    return board_type_list


def get_xml_configs(user_defined=False):
    """
    get xml config related variables
    :return: board_info, board_config, scenario_config, launch_config
    """

    config_path = None
    board_info = current_app.config.get('BOARD_INFO')
    board_type = get_board_type(board_info)
    if board_type is not None:
        config_path = os.path.join(current_app.config.get('CONFIG_PATH'), board_type)

    scenario_config = XmlConfig(config_path, not user_defined)
    launch_config = XmlConfig(config_path, not user_defined)

    return board_info, board_type, scenario_config, launch_config


def get_generic_scenario_config(scenario_config, add_vm_type=None):

    if add_vm_type is not None:
        vm_dict = {
            'PRE_STD_VM': ('partitioned', 'vm:id=0'),
            'PRE_RT_VM': ('hybrid_rt', 'vm:id=0'),
            'SAFETY_VM': ('hybrid', 'vm:id=0'),
            'SERVICE_VM': ('shared', 'vm:id=0'),
            'POST_STD_VM': ('shared', 'vm:id=1'),
            'POST_RT_VM': ('shared', 'vm:id=2'),
            'LAUNCH_POST_STD_VM': ('hybrid_launch_2user_vm', 'user_vm:id=1'),
            'LAUNCH_POST_RT_VM': ('shared_launch_6user_vm', 'user_vm:id=2')
        }
        config_path = os.path.join(current_app.config.get('DEFAULT_CONFIG_PATH'), 'generic_board')
        xml_path = os.path.join(config_path, vm_dict[add_vm_type][0] + '.xml')
        if os.path.isfile(xml_path):
            xsd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'schema', 'config.xsd')
            output_xml = os.path.join(config_path, vm_dict[add_vm_type][0] + '_1' + '.xml')
            default_populator.main(xsd_path, xml_path, output_xml)
            generic_scenario_config = XmlConfig(config_path)
            generic_scenario_config.set_curr(vm_dict[add_vm_type][0] + '_1')
            generic_scenario_config = set_default_config(generic_scenario_config)
            os.remove(output_xml)
            return generic_scenario_config.get_curr_elem(vm_dict[add_vm_type][1])
        else:
            return None
    config_path = os.path.join(current_app.config.get('CONFIG_PATH'), 'generic_board')
    generic_scenario_config = XmlConfig(config_path)
    for file in os.listdir(config_path):
        if os.path.isfile(os.path.join(config_path, file)) and \
                os.path.splitext(file)[1] == '.xml':
            generic_scenario_config.set_curr(os.path.splitext(file)[0])
            generic_scenario_config_root = generic_scenario_config.get_curr_root()
            if 'scenario' in generic_scenario_config_root.attrib \
                and 'user_vm_launcher' not in generic_scenario_config_root.attrib \
                and generic_scenario_config_root.attrib['scenario'] == \
                    scenario_config.get_curr_root().attrib['scenario']:
                return generic_scenario_config

    return None


def get_board_config(board_info):
    """
    get board config
    :param board_info: the board info file
    :return: the board type
    """
    board_config = None
    if board_info is not None:
        board_config = XmlConfig(os.path.join(current_app.config.get('CONFIG_PATH'), board_info), board_info)
        board_config.set_curr(board_info)

    return board_config


def get_board_type(board_info):
    """
    get board info type
    :param board_info: the board info file
    :return: the board type
    """
    board_config = get_board_config(board_info)
    board_type = None

    if board_config is not None:
        board_info_root = board_config.get_curr_root()
        if board_info_root is not None and 'board' in board_info_root.attrib:
            board_type = board_info_root.attrib['board']

    return board_type


def get_board_info(board_info):
    """
    get board info type
    :param board_info: the board info file
    :return: the board info
    """
    board_config = get_board_config(board_info)
    bios_info = None
    base_board_info = None
    if board_config is not None:
        board_info_root = board_config.get_curr_root()
        if board_info_root is not None:
            for item in list(board_info_root):
                if item.tag == 'BIOS_INFO':
                    for line in item.text.split('\n'):
                        if line.strip() != '':
                            if bios_info is None:
                                bios_info = line.strip()
                            else:
                                bios_info += ('\n' + line.strip())
                elif item.tag == 'BASE_BOARD_INFO':
                    for line in item.text.split('\n'):
                        if line.strip() != '':
                            if base_board_info is None:
                                base_board_info = line.strip()
                            else:
                                base_board_info += ('\n' + line.strip())

    return (bios_info, base_board_info)


def get_num_of_rdt_res(board_file_name, cdp_enalbed):
    """
    get the number of rdt res entries
    :param board_file_name: the file name of the board
    :param cdp_enalbed: cdp enalbed or not
    :return: the number of rdt res entries
    """
    dict_rdt_res_clos_max = get_board_rdt_res_clos_max(board_file_name)

    num_clos_max = 0
    num_mba_delay = 0

    if 'MBA' not in dict_rdt_res_clos_max.keys():
        num_mba_delay = 0
        if 'L2' not in dict_rdt_res_clos_max.keys() and 'L3' not in dict_rdt_res_clos_max.keys():
            num_clos_max = 0
        else:
            num_clos_max = min(dict_rdt_res_clos_max.values())
    else:
        if 'L2' not in dict_rdt_res_clos_max.keys() and 'L3' not in dict_rdt_res_clos_max.keys():
            num_clos_max = 0
            num_mba_delay = dict_rdt_res_clos_max['MBA']
        else:
            if cdp_enalbed is not None and cdp_enalbed.strip().lower() == 'y':
                for key in dict_rdt_res_clos_max.keys():
                    if key not in ['MBA']:
                        dict_rdt_res_clos_max[key] = int(dict_rdt_res_clos_max[key] / 2)
                common_clos_max = min(dict_rdt_res_clos_max.values())
                num_clos_max = common_clos_max * 2
                num_mba_delay = common_clos_max
            else:
                common_clos_max = min(dict_rdt_res_clos_max.values())
                num_clos_max = common_clos_max
                num_mba_delay = common_clos_max

    return (num_clos_max, num_mba_delay)


def get_board_rdt_res_clos_max(board_file_name):
    """
    get rdt res clos max of the board
    :param board_file_name: the file name of the board
    :return: the rdt res clos max
    """
    board_config = get_board_config(board_file_name)
    rdt_res_supported = []
    rdt_res_clos_max = []

    if board_config is not None:
        board_info_root = board_config.get_curr_root()
        if board_info_root is not None:
            for item in list(board_info_root):
                if item.tag == 'CLOS_INFO':
                    for line in item.text.split('\n'):
                        line = line.strip()
                        if line.startswith('rdt resources supported'):
                            try:
                                rdt_res_supported = line.split(':')[1].split(',')
                            except:
                                pass
                        if line.startswith('rdt resource clos max:'):
                            try:
                                rdt_res_clos_max = line.split(':')[1].split(',')
                                break
                            except:
                                pass
    if len(rdt_res_clos_max) < len(rdt_res_supported):
        for i in range(len(rdt_res_supported) - len(rdt_res_clos_max)):
            rdt_res_clos_max.append(0)
    dict_rdt_res_clos_max = {}
    for i in range(len(rdt_res_supported)):
        try:
            clos_max = int(rdt_res_clos_max[i].strip())
        except:
            clos_max = 0
        if clos_max > 0:
            dict_rdt_res_clos_max[rdt_res_supported[i].strip()] = clos_max
    return dict_rdt_res_clos_max


def assign_vm_id(scenario_config):
    """
    assign vm ids for the scenario setting.
    :param scenario_config:
    :return:
    """
    root = scenario_config.get_curr_root()
    pre_launched_vm_num = 0
    sos_vm_num = 0
    post_launched_vm_num = 0

    for vm in list(root):
        if vm.tag == 'vm':
            for item in list(vm):
                if item.tag == 'vm_type':
                    if item.text in ['PRE_STD_VM', 'SAFETY_VM', 'PRE_RT_VM']:
                        pre_launched_vm_num += 1
                    elif item.text in ['SERVICE_VM']:
                        sos_vm_num += 1
                    elif item.text in ['POST_STD_VM', 'POST_RT_VM']:
                        post_launched_vm_num += 1

    pre_launched_vm_index = 0
    sos_vm_index = pre_launched_vm_num
    post_launched_vm_index = pre_launched_vm_num + sos_vm_num
    for vm in list(root):
        if vm.tag == 'vm':
            for item in list(vm):
                if item.tag == 'vm_type':
                    if item.text in ['PRE_STD_VM', 'SAFETY_VM', 'PRE_RT_VM']:
                        vm.attrib['id'] = str(pre_launched_vm_index)
                        pre_launched_vm_index += 1
                    elif item.text in ['SERVICE_VM']:
                        vm.attrib['id'] = str(sos_vm_index)
                        sos_vm_index += 1
                    elif item.text in ['POST_STD_VM', 'POST_RT_VM']:
                        vm.attrib['id'] = str(post_launched_vm_index)
                        post_launched_vm_index += 1


def get_xpath_dict_of_xsd():
    """
    get xpath_dict of the xsd config
    :return: xpath dict
    """
    acrn_config_element_root = get_acrn_config_element(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'schema', 'config.xsd'))
    xpath_dict = acrn_config_element_2_xpath_dict(acrn_config_element_root, {})
    return xpath_dict


def set_default_config(config):
    '''
    set default values for current config
    :param config: the current config
    :return: the return config setting with default values
    '''
    xpath_dict = get_xpath_dict_of_xsd()
    config_root = config.get_curr_root()

    return set_default_config_for_curr_layer(config, config_root, '/'+config_root.tag, xpath_dict)


def set_default_config_for_curr_layer(config, elem, key, xpath_dict):
    for sub_elem in list(elem):
        sub_key = key+'/'+sub_elem.tag
        if sub_key in xpath_dict.keys() and xpath_dict[sub_key] and xpath_dict[sub_key]['default']:
            config.set_curr_value(xpath_dict[sub_key]['default'], *tuple(sub_key.split('/')[2:]))
        set_default_config_for_curr_layer(config, sub_elem, sub_key, xpath_dict)
    return config


def get_generic_config_list():
    default_config_path = os.path.join(current_app.config.get('DEFAULT_CONFIG_PATH'), 'generic_board')
    default_xml_config = XmlConfig(default_config_path)
    secenario_config_list = []
    launch_config_list = []
    for config_name in os.listdir(default_config_path):
        if os.path.isfile(os.path.join(default_config_path, config_name)):
            default_xml_config.set_curr(config_name.rsplit('.', 1)[0])
            xml_config_root = default_xml_config.get_curr_root()
            if 'scenario' in xml_config_root.attrib and 'user_vm_launcher' not in xml_config_root.attrib:
                secenario_config_list.append(config_name.rsplit('.', 1)[0])
            elif 'scenario' in xml_config_root.attrib and 'user_vm_launcher' in xml_config_root.attrib:
                launch_config_list.append(config_name.rsplit('.', 1)[0])

    return (secenario_config_list, launch_config_list)


@CONFIG_APP.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))

    return dict(mdebug=print_in_console)
