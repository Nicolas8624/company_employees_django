using CompanyEmployees01.Entities;
using CompanyEmployees01.Service;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace CompanyEmployees01.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class GamesController : ControllerBase
    {
        [HttpGet]
        // GET
        public Player GET()
        {
            // Generar Acoplamiento. Mala práctica. Se crea una instancia de la clase PlayerGenerator a través del operador new
            var playerGenerator = new PlayerGenerator();
            var newPlayer = playerGenerator.CreateNewPlayer();
            return newPlayer;
        }
    }
}
