using Microsoft.Extensions.Hosting;

var builder = DistributedApplication.CreateBuilder(args);

#pragma warning disable ASPIREHOSTINGPYTHON001
var pythonapp = builder.AddPythonApp("dokusharp-engine", "../DOKUSHArp.Engine", "main.py")
	   .WithHttpEndpoint(env: "PORT")
	   .WithExternalHttpEndpoints()
	   .WithOtlpExporter();
#pragma warning restore ASPIREHOSTINGPYTHON001

builder.AddProject<Projects.DOKUSHArp_Web>("dokusharp-web")
	.WithExternalHttpEndpoints()
	.WithEnvironment("engine", pythonapp.GetEndpoint("http"))
	.WithReference(pythonapp);

if (builder.ExecutionContext.IsRunMode && builder.Environment.IsDevelopment())
{
	pythonapp.WithEnvironment("DEBUG", "True");
}

builder.Build().Run();
