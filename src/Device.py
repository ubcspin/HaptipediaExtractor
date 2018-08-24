from CrossReference import modify_name
devices = {}


class Device:

    def __init__(self, name, pdf):
        self.name = name  # also the name of the folder it's in
        self.key = modify_name(name)
        self.refs = [] # a list of reference objects
        self.ref_titles = [] # a list of reference object titles
        self.forward_refs = []
        self.backward_refs = []
        self.authors = []
        self.affiliates = []
        self.abstract = ''
        self.date = ''
        self.publisher = ''
        self.sections = {} # name + '/Sections/Section.txt'
        self.figures = {} # name + '/Figures/'
        self.pdf = pdf


def init_device(name, pdf):
    new_device = Device(name, pdf)
    modified_name = modify_name(name)
    count = 1
    while modified_name in devices:
        modified_name = modified_name + ' (' +str(count) + ')'
        count += 1
    devices[modified_name] = new_device

    return new_device, modified_name


def update_name(new_name, device):
    device.name = new_name
    device.key = modify_name(new_name)


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
