# PentiumTool library
from pentiumtool.tools import PentiumLocalToolClass
from pentiumtool.exceptions import Exceptions

# Third-party library
from neo4j.v1 import GraphDatabase

# Here is a local demo subclass of PentiumTool, if you are ready to deploy,
# PLEASE NOTE to change superclass as [PentiumToolClass]
class PentiumDevTool(PentiumLocalToolClass):

    # ========== Developer MUST implement verify function for each tool ==========
    def verify(self):
        self.isValid = True
        
        # Info from PentiumToolClass
        # This can retrieve params of event context
        self.toolParams = self.jobContext.getParams()
        # This can retrieve toolId of event context
        self.toolId = self.jobContext.getToolId()
        self.notifyId = self.jobQueue.getNotifyId()
        self.toolResults = self.jobQueue.getResults()

        requiredKeys = {
            "input": str
        }
        try:            
            # Make sure required keys are available
            if all(key in self.toolParams for key in requiredKeys.keys()):
                # validate type of required keys in params
                for key in requiredKeys:
                    if type(self.toolParams[key]) != requiredKeys[key]:
                        raise Exceptions.InvalidParamError("Type error of params in workflows", self.loggingInfo())
                
            else:
                raise Exceptions.InvalidParamError("Required keys in params of workflows are missing.", self.loggingInfo())

        except Exception as e:
            self.isValid = False
            # Save processing results to yourTool with Id
            self.toolResults[self.toolId]["statusCode"] = 500
            self.toolResults[self.toolId]["body"] = str(e)
            self.toolResults[self.notifyId]["message"] = str(e)

    # ========== Developer MUST implement process function for each tool ==========
    def process(self):
        if self.isValid:
            # connect to neo4jDB
            driver = GraphDatabase.driver("bolt://34.215.102.35:7687", auth=("neo4j", "neo4j"))
            session = driver.session()
            session.run("CREATE (n:Pentium {Name: 'computer', Status: 'O'})")

            message =  "Hello world! " + self.toolParams["input"]
            # Save processing results to yourTool with Id
            self.toolResults[self.toolId]["statusCode"] = 200
            self.toolResults[self.toolId]["body"] = message
            # notify message to nextTool with Id
            self.toolResults[self.notifyId]["message"] = message
        else:
            pass


# Here is function name for launching lambda
def lambdaHandler(event, context):
    devClass = PentiumDevTool()
    response = devClass.invoke(event)
    return response.getResponse()


# Simulated data spec of input and output
if __name__=="__main__":
    context = {
        "queue": [
            {
                "conditions": [],
                "params": {
                # Write down any input key/value of params here.
                    "input": "Apple!!!",
                },
                "toolId": "yourToolId"
            },
            {
                "conditions": [],
                "params": {
                    "input": "Here is another tool for input params"
                },
                "toolId": "nextToolId"
            }
        ],
        "results": {
            "yourToolId": {
            # Here is any key/value of results which process() implement by yourself.
                "key1": ""
            },
            "nextToolId": {
                "key2": ""
            }
        }
    }

    # Run local lambda function
    lambdaHandler(context, "")

