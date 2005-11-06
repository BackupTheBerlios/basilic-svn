import string, sys

def do_apply(sin, sout, vars):
    """Read sin file, replace vars arguments, and write to sout file."""
    for line in sin.readlines():
        sout.write(line % vars)
    sout.flush()
    sout.close()
    sin.close()

if __name__=="__main__":
    argv=sys.argv
    if len(argv)==0:
        print "Usage : "
        print "$ apply.py params"
        print "params are name1=value1 name2=value2"
        print ""
        print "apply the params to the text from stdin, outputting to stdout"
    else:
        args={}
        for arg in sys.argv[1:]:
            (name,value)=arg.split('=')
            args[name]=value
        do_apply(sys.stdin, sys.stdout, args)


