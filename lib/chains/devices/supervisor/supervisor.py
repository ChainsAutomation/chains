def server_state(server):
    cur_state = server.supervisor.getState()
    print cur_state


def server_shutdown():
    pass


def server_restart():
    pass


def state(server):
    cur_state = server.supervisor.getState()
    print cur_state


def stop(program):
    pass


def stop_all(program):
    pass


def stop_group(group):
    pass


def start(program):
    pass


def start_all(program):
    pass


def start_group(group):
    pass


def restart(program):
    pass


def restart_group(group):
    pass
