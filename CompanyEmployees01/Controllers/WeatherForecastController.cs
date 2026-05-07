using Contracts;
using Microsoft.AspNetCore.Mvc;

namespace CompanyEmployees01.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class WeatherForecastController : ControllerBase
    {
        // Preparativo para la Inyección de dependencias
        private readonly ILoggerManager _loggerManager; //Campo

        public WeatherForecastController(ILoggerManager logger) // Parámetro
        {
            this._loggerManager = logger;
        }
        //Fin Preparativo

        private static readonly string[] Summaries =
        [
            "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
        ];

        [HttpGet]
        public IEnumerable<WeatherForecast> Get()
        {
            _loggerManager.LogDebug("This is a debug message. Power by V.C.A.");
            _loggerManager.LogInformation("This is an information. Power by V.C.A.");
            _loggerManager.LogWarning("This is a warn message. Power by V.C.A.");
            _loggerManager.LogError("This is an error message. Power by V.C.A.");

            return Enumerable.Range(1, 5).Select(index => new WeatherForecast
            {
                Date = DateOnly.FromDateTime(DateTime.Now.AddDays(index)),
                TemperatureC = Random.Shared.Next(-20, 55),
                Summary = Summaries[Random.Shared.Next(Summaries.Length)]
            })
            .ToArray();
        }
    }
}
