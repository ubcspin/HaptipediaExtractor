from CrossReference import modify_name
devices = {}


class Device:

    def __init__(self, name):
        self.name = name  # also the name of the folder it's in
        self.backward_ref = {} # name of ref is key, value is the number of times ref was cited
        self.forward_ref = {} # name of ref is key, value is the number of times ref was cited
        self.authors = []
        self.date = ''
        self.publisher = ''
        self.sections = {}
        self.figures = {}
        self.citations = []


def init_device(name):
    new_device = Device(name)
    modified_name = modify_name(name)
    if modified_name in devices:
        modified_name = modified_name + ' (1)'
    devices[modified_name] = new_device

    return new_device, modified_name


def update_key(date, device_key):
    new_key = device_key[:-3] + '(' + date + ')'
    devices[new_key] = devices[device_key]
    del devices[device_key]


# Parameters:
# device: device where backwardRef should be added
# ref_name: name of the reference (not modified)
def add_backward_ref(device, ref):
    ref_name = modify_name(ref.title)
    ref_occurance = ref.timesCited
    device.backward_ref[ref_name] = ref_occurance


def get_devices():
    return devices