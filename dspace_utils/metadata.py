# 3rd party library imports

# local imports
from .common import DSpaceCommon


class MetadataDumper(DSpaceCommon):
    """
    Print item metadata
    """
    def __init__(self, handle, verbose='info'):
        super().__init__(verbose)

        self.item = self.get_item_from_handle(handle)

    def __str__(self):
        lines = []

        lines.append(f'name: {self.item.name}')
        lines.append(f'type: {self.item.type}')
        lines.append(f'handle: {self.item.handle}')
        lines.append(f'inArchive: {self.item.inArchive}')
        lines.append(f'uuid: {self.item.uuid}')
        lines.append(f'withdrawn: {self.item.withdrawn}')
        lines.append('metadata:')

        for key, values in self.item.metadata.items():
            lines.append(f'    {key}:')
            for item_value in values:
                for sub_item in item_value['value'].splitlines():
                    lines.append(f'        {sub_item}')
                if len(item_value['value'].splitlines()) > 1:
                    lines.append('')

        return '\n'.join(lines)

    def run(self):
        pass
