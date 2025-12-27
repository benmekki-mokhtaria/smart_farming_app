classDiagram

&nbsp;   class Utilisateur {

&nbsp;       +int id

&nbsp;       +string username

&nbsp;       +string password

&nbsp;   }

&nbsp;   class Analyse\_IA {

&nbsp;       +int id

&nbsp;       +float n\_val

&nbsp;       +float p\_val

&nbsp;       +float k\_val

&nbsp;       +float temperature

&nbsp;       +float result

&nbsp;   }

&nbsp;   Utilisateur "1" -- "\*" Analyse\_IA : effectue

