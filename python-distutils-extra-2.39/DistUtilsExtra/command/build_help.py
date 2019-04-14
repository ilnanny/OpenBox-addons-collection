'''Implement the Distutils "build_help" command.'''

from glob import glob
import os.path
import distutils.cmd

class build_help(distutils.cmd.Command):
    description = 'install Mallard or DocBook XML based documentation'
    user_options= [('help-dir', None, 'help directory in the source tree')]
	
    def initialize_options(self):
        self.help_dir = None

    def finalize_options(self):
        if self.help_dir is None:
            self.help_dir = 'help'

    def get_data_files(self):
        data_files = []
        name = self.distribution.metadata.name

        for path in glob(os.path.join(self.help_dir, '*')):
            lang = os.path.basename(path)
            path_xml = os.path.join('share/help', lang, name)
            path_figures = os.path.join('share/help', lang, name, 'figures')
            
            docbook_files = glob('%s/index.docbook' % path)
            docbook_files_extra = glob('%s/*.xml' % path)
            mallard_files = glob('%s/*.page' % path)
            data_files.append((path_xml, docbook_files + docbook_files_extra + mallard_files))
            data_files.append((path_figures, glob('%s/figures/*.png' % path)))
        
        return data_files
    
    def run(self):
        self.announce('Setting up help files...')
        
        data_files = self.distribution.data_files
        data_files.extend(self.get_data_files())
