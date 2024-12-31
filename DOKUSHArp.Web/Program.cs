using DOKUSHArp.Web.Components;
using DOKUSHArp.Web.Services;

var builder = WebApplication.CreateBuilder(args);

builder.AddServiceDefaults();

// Add services to the container.
builder.Services.AddRazorComponents();
builder.Services.AddHttpClient<MangaService>(client => client.BaseAddress = new Uri("https+http://dokusharp-engine"));
builder.Services.Configure<EngineOptions>(options => options.EngineBasePath = builder.Configuration["engine"]!);

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
app.MapRazorComponents<App>();

app.Run();
