import math

def BinomialErrorStat(n_all, n_pass):
    return BinomialError(n_all, math.sqrt(n_all), n_pass, math.sqrt(n_pass))

# Calculate error on an efficiency, where 
# eff = n_pass / n_all
# n_all_err is the uncertainty on n_all etc
def BinomialError(n_all, n_all_err, n_pass, n_pass_err):
  eff = n_pass / n_all
  return math.sqrt(((1 - 2 * eff) * ( n_pass_err ) * ( n_pass_err) + eff * eff * n_all_err * n_all_err ) / (n_all * n_all))
