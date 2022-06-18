var miamicoin= 0.001569
var dollars=0
var amount=document.getElementById("amount");
var estimatedprice=0;

const checkbox = document.getElementById('myCheckbox')

checkbox.addEventListener('change', (event) => {
  if (event.currentTarget.checked) {
    typecost=1;
    document.getElementById("display").innerHTML ="You want to develop a website";
  } 
})

function displayprice(){
  estimatedprice=100*typecost;
  document.getElementById("estimatedprice").innerHTML ="estimatedprice";
}
function sliderpay(){

   dollars=miamicoin*amount;
   
}

function increaseapp(){
    app=app+1;
    dollars=dollars+100*typecost;
}

