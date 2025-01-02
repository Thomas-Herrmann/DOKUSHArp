using DOKUSHArp.Web.Components;
using DOKUSHArp.Web.Components.Store;
using DOKUSHArp.Web.Services;

var builder = WebApplication.CreateBuilder(args);

builder.AddServiceDefaults();

// Add services to the container.
builder.Services.AddRazorComponents().AddInteractiveServerComponents();
builder.Services.AddHttpClient<MangaService>(client => client.BaseAddress = new Uri("https+http://dokusharp-engine"));
builder.Services.Configure<EngineOptions>(options => options.EngineBasePath = builder.Configuration["engine"]!);

var stateTypes = typeof(Program).Assembly
    .GetTypes()
    .Where(type => !type.IsAbstract && type.GetInterfaces().Any(@interface => @interface.IsGenericType && @interface.GetGenericTypeDefinition() == typeof(IState<>) && @interface.GetGenericArguments()[0] == type));

builder.Services.AddScoped<Store>();

foreach (var stateType in stateTypes)
    builder.Services.AddScoped(typeof(State<>).MakeGenericType(stateType));

var app = builder.Build();

app.MapDefaultEndpoints();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseAntiforgery();
app.MapStaticAssets();
app.MapRazorComponents<App>().AddInteractiveServerRenderMode();

await app.RunAsync();