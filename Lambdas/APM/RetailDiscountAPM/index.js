const signalFxLambda = require('signalfx-lambda');
const tracing = require('signalfx-lambda/tracing'); // needed if we wish to set our own tags an/or wish to call other lambda's

exports.handler = signalFxLambda.asyncWrapper(async (event,context,callback) => {
try {
    console.log("Received event:", JSON.stringify(event, null, 2));
    const CustomerType = event.queryStringParameters.CustomerType;
    console.log ("type:",CustomerType)
    var response= {}; 
    const tracer = tracing.tracer();    // get the active tracer (only if you wish to use custom tags or call other lambda's)
    if (tracer){
        console.log ("We have a tracer");
    }
    else
    {
        console.error("No Tracer"); 
        response = {
           statusCode: 500,
           headers: {},
           body: "Tracer not available"
          };
    return response;
    }  
   const span = tracer.scope().active();  // get the active span (only if you wish to use custom tags)
    if (span){
        console.log ("We have a span");
        //We now can use span.setTag("tag_label", value) to set your own tags
        span.setTag("environment", process.env.SIGNALFX_APM_ENVIRONMENT) ///setting the env to your environment    
        span.setTag("Custom tag", "custom value");
    }
    else{
        console.error("No span");  
        response = {
            statusCode: 500,
            headers: {},
            body: "Span not available"
        };
    return response;
    }
   
   var discount= 0; // hardcoded.. could come from DB
   if (CustomerType ==="Gold"){
    discount= 29;
   }
   else if  (CustomerType === "Platinum"){
    discount= 99;
   }
   response = {
        statusCode: 200,
         body:JSON.stringify({'Discount': discount})
    };
    return response;
   }
catch (err) {
    console.error(err);
    } 
});
