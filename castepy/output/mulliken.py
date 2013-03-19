import sys
import re

class MullikenResult(object):
  re_block = re.compile(r"Species   Ion     s      p      d      f     Total  Charge \(e\)\n[=]+\n(.*?)\n[=]+", re.M | re.S)

  @classmethod
  def load(klass, castep_file):
    blocks = klass.re_block.findall(castep_file)

    results = []

    for block in blocks:
      result = MullikenResult()

      result.charges = {}
      lines = block.split('\n')

      for line in lines:
        line_s = line.split()
        s = line_s[0]
        i = int(line_s[1])
        charge_s, charge_p, charge_d, charge_f, tot, charge = map(float, line_s[2:])

        result.charges[(s,i)] = {'charge_s': charge_s,
                               'charge_p': charge_p,
                               'charge_d': charge_d,
                               'charge_f': charge_f,
                               'tot': tot,
                               'charge': charge,}
      results.append(result)

    return results

  def annotate(self, ions):
    for s, i in self.charges:
      ion = ions.get_species(s, i)
      ion.mulliken = self.charges[(s,i)]

if __name__ == "__main__":
  results = MullikenResult.load(open(sys.argv[1]).read())
  print results[0].charges

