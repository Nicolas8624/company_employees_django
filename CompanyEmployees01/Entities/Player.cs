namespace CompanyEmployees01.Entities
{
    public class Player
    {
        public string? Name { get; set; }
        public Gender Gender { get; set; }
        public int Age { get; set; }
        public HairColor HairColor { get; set; }
        public int Strength { get; set; }   //Fuerza
        public string? Race { get; set; }   // Raza
    }
}
