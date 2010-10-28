# -*- coding: utf-8 -*-
import os
import os.path

class Cell:
    def __init__(self, cell_file=None):
        self.blocks = {}
        self.other = []
        self.otherdict = {}

        if cell_file is not None:
            self.parse_cell(cell_file)

    def parse_cell(self, cell):
        import re
        block_re = re.compile(r"%block (.*?)\n(.*?\n{0,})%endblock (.*?)\n", re.I | re.S | re.M)

        blocks = block_re.findall(cell)
        
        for name, content, _ in blocks:
            unclean_lines = content.split('\n')
            lines = []
            for line in unclean_lines:
                line_clean = line.strip()
                if len(line_clean) > 0:
                    lines.append(line_clean)
            self.blocks[name.upper()] = lines

        cell_sans_blocks = block_re.sub("", cell)
        other = re.split("\n\s{0,}", cell_sans_blocks, re.S | re.M)
        for o in other:
            o_s = o.strip()
            if len(o_s) > 0:
                self.other.append(o_s)
                
                o_split = re.split("[\s:]+", o_s, maxsplit=1)

                if len(o_split) == 2:
                    self.otherdict[o_split[0]] = o_split[1]

        self.ions = []
        self.ion_index = {}
	
	if 'POSITIONS_ABS' in self.blocks:
	        self.ions_type = 'POSITIONS_ABS'
	elif 'POSITIONS_FRAC' in self.blocks:
		self.ions_type = 'POSITIONS_FRAC'
	
        self.ions_units = ''
        for line in self.blocks[self.ions_type]: # Include positions frac
            lsplit = line.split()

            if len(lsplit) == 4:
                species, x, y, z = lsplit
                
                ion = (species, (float(x), float(y), float(z)))
                self.ions.append(ion)
            elif len(lsplit) == 1:
                self.ions_units = lsplit[0]
                
        self.ion_index = self.make_ion_index()

    def make_ion_index(self):
        ion_index = {}
        for ion in self.ions:
            if ion[0] in ion_index:
                ion_index[ion[0]].append(ion)
            else:
                ion_index[ion[0]] = [ion,]
        return ion_index

    def hack_perturb_origin(self):
        """ Hack to move the perturbing NMR nucleus onto the origin """
        j_site = self.otherdict['jcoupling_site'].split()
        
        j_site_ion = self.ion_index[j_site[0]][int(j_site[1])-1]
        
        
        ions_prime = []
        for species, pos in self.ions:
            new_ion = (species, (pos[0]-j_site_ion[1][0],
                                 pos[1]-j_site_ion[1][1],
                                 pos[2]-j_site_ion[1][2],))
            ions_prime.append(new_ion)

        self.ions = ions_prime
        self.ion_index = self.make_ion_index()

        self.blocks[self.ions_type] = [self.ions_units] + ["%s %f %f %f" % (s, x, y, z) for (s, (x, y, z)) in self.ions]

    def __str__(self):
        s  = ""
        for name, lines in self.blocks.items():
            s += "%%block %s\n" % name
            s += "\n".join(lines)
            s += "\n%%endblock %s\n\n" % name

        for line in self.other:
            s += "%s\n" % line

        return s
        
class Parameters:
    def __init__(self, params=None):
        if params is not None:
            if type(params) is dict:
              self.params = params
            elif type(params) is str:
              self.params = self.parse_params(params)
            elif type(params) is file:
              self.params = self.parse_params(params.read())
        else:
            self.params = {}

    def parse_params(self, params):
        import re
        split_re = re.compile("\s+[=:]\s+")
        plines = params.split("\n")

        params = {}
        for pline in plines:
            nv = split_re.split(pline)
            
            if len(nv) == 2:
                params[nv[0].strip()] = nv[1].strip()
        
        return params

    def __setitem__(self, n, v):
        self.params[n] = v
    
    def __getitem__(self, n):
        if n in self.params:
            return self.params[n]
        else:
            raise KeyError;

    def __str__(self):
        return "\n".join(["%s: %s" % (n ,v) for n, v in self.params.items()])

class Calculation:
    def __init__(self, cell=None, param=None, cell_file_path=None, param_file_path=None, required_files=[]):
        self.cell = cell
        self.param = param
        
        self.dir_path = None
        self.cell_file_name = "seed.cell"
        self.param_file_name = "seed.param"

        # Files to link into execution directory
        self.required_files = set(required_files)

        # We're given a cell file to load from
        if cell_file_path is not None:
            self.cell_file_path = os.path.abspath(cell_file_path)
            _, self.cell_file_name = os.path.split(cell_file_path)
            
            # If we don't have a cell loaded, and we have a cell file, load cell from that cell file
            if self.cell is None:
                self.cell = Cell(open(self.cell_file_path).read())
            else:
                self.cell = ""
        else:
            self.cell_file_name = "seed.cell"

        # We're given a param file to load from
        if param_file_path is not None:
            self.param_file_path = os.path.abspath(param_file_path)
            _, self.param_file_name = os.path.split(param_file_path)
            
            # If we don't have a param loaded, and we have a param file, load param from that param file
            if self.param is None:
                self.param = Parameters(open(self.param_file_path))
            else:
                self.param = ""
        else:
            self.param_file_name = "seed.param"

        self.seed_name = self.param_file_name.split(".")[0]
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        """ This ensures it's cleaned up, even if there's an exception """
        # self.clean()
        return False

    def make_dir(self, prefix="tmp"):
        """
            Make a temporary directory for Castep to do calculations in
        """
        import tempfile

        if self.dir_path is None:
            self.dir_path = tempfile.mkdtemp(dir="./tmp", prefix=prefix)

    def link_required_files(self, dir_path):
        for f in self.required_files:
            f = os.path.abspath(f)            
            d, filename = os.path.split(f)
            target = os.path.join(dir_path, filename)
            os.symlink(f, target)
            
            # print os.getcwd(), f, target

    def write_seed(self):
        """
            Write the seed files seed.cell and seed.param based on provided
            input structures (which could be objects or strings)
        """
        self.cell_file = open(os.path.join(self.dir_path, self.cell_file_name), "w+")
        self.param_file = open(os.path.join(self.dir_path, self.param_file_name), "w+")

        self.cell_file.write("%s" % self.cell)
        self.param_file.write("%s" % self.param)

        self.cell_file.flush()
        os.fsync(self.cell_file)
        self.param_file.flush()
        os.fsync(self.param_file)

        self.link_required_files(self.dir_path)

    def write(self, prefix="tmp", dir_path=None):
        """
            Prepare the temporary directory and seed files
        """
        if dir_path is None:
          self.make_dir(prefix)
        else:
          self.dir_path = dir_path
          if not os.path.isdir(dir_path):
              os.mkdir(dir_path)
          
        self.write_seed()
    
    def clean(self):
        """
            Clean up our directory
        """
        import shutil
        
        self.cell_file.close()
        self.param_file.close()
        shutil.rmtree(self.dir_path)

class SimpleCalculation:
    def __init__(self, dir_path, seed_name="seed"):
        self.dir_path = dir_path
        self.seed_name = seed_name

    def has_run(self):
        if os.path.exists(os.path.join(self.dir_path, self.seed_name + ".castep")):
	    return True
        else:
            return False

class Castep:
    castep_path = "/users2/green/CASTEP-5.5/obj/linux_x86_64_ifort11/castep"
    sge_command = "qsub"
    sge_script = "/home/green/test_runs/run_mpi.sh"

    def __init__(self, castep_path=""):
        self.castep_path = castep_path
    
    def execute(self, calculation):
        """
            Execute Castep in our temporary directory via the shell
        """
        import subprocess

        retcode = subprocess.call([self.castep_path, calculation.seed_name], cwd=calculation.dir_path)

    def sge_execute(self, calculation, num_nodes=1):
        import subprocess

	retcode = subprocess.call([self.sge_command, self.sge_script, calculation.seed_name, num_nodes*8], cwd=calculation.dir_path)

