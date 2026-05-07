using CompanyEmployees01.Contracts;
using CompanyEmployees01.Entities;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace CompanyEmployees01.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class Games2Controller : ControllerBase
    {
        // Campo de tipo Interface
        private readonly IPlayerGenerator _playerGenerator;

        // Constructor de la clase (Constructor del controlador)
        // Sobrecarga del constructor

        public Games2Controller(IPlayerGenerator playerGenerator) //Parámetro del constructor
        {
            _playerGenerator = playerGenerator;
        }

        // Rompe el acoplamiento y privilegia la Cohesión
        [HttpGet]
        public Player GET()
        {
            var newPlayer = this._playerGenerator.CreateNewPlayer();
            return newPlayer;
        }
    }
}
