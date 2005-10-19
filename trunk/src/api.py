import basilic

operations=[
    "request",
    "test",
    "debug",
    ]
    
operators=[
    "+",  
    "-",
    "?",
    ]

def operation_test(basilic,stream,params):
    stream.write('OK\n')
    stream.write('---\n')
    stream.write(basilic.version.full_copyright)        
    
def operation_request(basilic,stream,userlogin=None,userbase=None,tags=[],format="xml"):
    stream.write('<!DOCTYPE xml PUBLIC>')
    stream.write("<yes>no</yes>")