*{

margin:0;

padding:0;

box-sizing:border-box;

font-family:Segoe UI;

}

body{

display:flex;

background:#eef2f7;

}

.sidebar{

width:250px;

background:#0f172a;

height:100vh;

position:fixed;

padding-top:25px;

}

.logo{

color:white;

text-align:center;

margin-bottom:40px;

}

.logo span{

font-size:13px;

color:#bbb;

}

.sidebar a{

display:block;

padding:15px 25px;

color:white;

text-decoration:none;

transition:.3s;

}

.sidebar a:hover{

background:#2563eb;

padding-left:35px;

}

.main{

margin-left:250px;

width:100%;

padding:25px;

}

.topbar{

display:flex;

justify-content:space-between;

align-items:center;

background:white;

padding:20px;

border-radius:15px;

box-shadow:0 4px 15px rgba(0,0,0,.08);

}

.cards{

display:grid;

grid-template-columns:repeat(4,1fr);

gap:20px;

margin-top:30px;

}

.card{

background:white;

padding:25px;

border-radius:15px;

box-shadow:0 5px 15px rgba(0,0,0,.08);

}

.card h3{

color:#666;

}

.card h1{

margin-top:10px;

color:#2563eb;

}

.tablebox{

margin-top:35px;

background:white;

padding:20px;

border-radius:15px;

box-shadow:0 5px 15px rgba(0,0,0,.08);

}

table{

width:100%;

margin-top:20px;

border-collapse:collapse;

}

th{

background:#2563eb;

color:white;

padding:12px;

}

td{

padding:12px;

border-bottom:1px solid #eee;

}