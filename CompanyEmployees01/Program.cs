using CompanyEmployees01.Contracts;
using CompanyEmployees01.Extensions;
using CompanyEmployees01.Service;
using Contracts;
using LoggingService;
using Serilog;

var builder = WebApplication.CreateBuilder(args);



// Add services to the container.
builder.Services.AddScoped<IPlayerGenerator, PlayerGenerator2>();
builder.Services.ConfigureCors();
builder.Services.ConfigureIISIntegration();

// New 
builder.Services.ConfigureLoggerService();

builder.Services.AddControllers();

// Configure Serilog for the Host early so Log.Logger is available for DI registrations
builder.Host.UseSerilog((hostContext, configuration) =>
{
    configuration.ReadFrom.Configuration(hostContext.Configuration);
});

var app = builder.Build();

// Reenviará los encabezados del proxy a la solicitud actual.
// Esto nos ayudará durante el despliegue de la aplicación. Tenga en cuenta que necesitamos
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}else
    app.UseHsts();  // Se añadirá un middleware para el uso de HSTS, que agrega el encabezado Strict-Transport-Security

// Configure the HTTP request pipeline.

app.UseHttpsRedirection();

// Permite usar archivos estáticos para la solicitud.
// Si no especificamos una ruta al directorio de archivos estáticos, utilizará una carpeta wwwroot de nuestro proyecto por defecto.
app.UseStaticFiles();

// New
app.UseForwardedHeaders(new ForwardedHeadersOptions
{
    ForwardedHeaders = Microsoft.AspNetCore.HttpOverrides.ForwardedHeaders.All
});

// New
app.UseCors("CorsPolicy");

app.UseAuthorization();

//app.Run(async contex =>
// await contex.Response.WriteAsync("Hello from the middleware component.")
//);

app.MapControllers();

app.Run();
