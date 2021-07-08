import signalfx_lambda
import opentracing
from opentracing.ext import tags
from opentracing.propagation import Format


import json
import uuid
import os
APM_ENVIRONMENT = os.environ['SIGNALFX_APM_ENVIRONMENT']
LAMBDA_FUNCTION = os.environ['LAMBDA_FUNCTION_NAME']

@signalfx_lambda.emits_metrics()
@signalfx_lambda.is_traced(with_span=False)
def lambda_handler(event, context):
    # Setup tracer so we can create span and set the B3 Headers
    print ("event: ", event)
    tracer = opentracing.tracer
    TraceHeaders =  event ['TraceHeaders']  # Value passed in from  calling app
    print ("TraceHeaders: ", TraceHeaders)
    span_ctx = tracer.extract(Format.HTTP_HEADERS, TraceHeaders)
    print("span_ctx: ", span_ctx)
    span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER, "environment" : APM_ENVIRONMENT}
    with tracer.start_active_span(LAMBDA_FUNCTION , child_of=span_ctx, tags=span_tags):
        span = tracer.active_span #grabing the active span for Custom Tags
        print ("Span: ", span)
        with tracer.start_active_span(LAMBDA_FUNCTION+"_input", tags=span_tags) as scope:
            scopespan = scope.span
        
            #1 Read the input parameters
            productName = event['ProductName']
            quantity    = event['Quantity']
            unitPrice   = event['UnitPrice']
        
            #send tags and close span
            scopespan.set_tag("ProductName",productName)
            scopespan.set_tag("Quantity", quantity)
            scopespan.set_tag("UnitPrice", unitPrice)
            
         
        with tracer.start_active_span(LAMBDA_FUNCTION+"_transaction", tags=span_tags) as scope:
            scopespan = scope.span
         
            #2 Generate the Order Transaction ID
            transactionId   = str(uuid.uuid1())
    
            #send tags and close span
            scopespan.set_tag("TransactionId",transactionId)
            scope.close()
       
        with tracer.start_active_span(LAMBDA_FUNCTION+"_Logic", tags=span_tags) as scope:
            scopespan = scope.span
         
            #3 Implement Business Logic
            amount      = quantity * unitPrice
            
            #send tags and close span
            scopespan.set_tag("Amount",amount)
            scope.close()
        
        if productName== "Bad Phone":
            with tracer.start_active_span(LAMBDA_FUNCTION+"_error", tags=span_tags) as scope:  
                scopespan = scope.span
                #3 Implement Error Scenario
                scopespan.set_tags("error", True)
                scopespan.set_tag("log","Phone type is unusable for this customer type")
                scopespan.set_tag("ProductName",productName)
                scopespan.set_tag("Quantity", quantity)
                scopespan.set_tag("UnitPrice", unitPrice)
                scopespan.set_tag("TransactionId",transactionId)
                if amount == 800:
                     #when buying two bad phones as platinum force code error as set_tag doens't exist
                     scopescan.set_tags("error_msg","This is a conditional coding error")
                scope.close()
        #optionally close the span
        span.finish()
        #4 Format and return the result
       
        return {
            'TransactionID' :   transactionId,
            'ProductName'   :   productName,
            'Amount'        :   amount
            
            }