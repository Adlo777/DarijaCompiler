
let pierre = {
    'nom' : 'Pierre',
    'age' : 29,
    'sport' : 'danse',
    'cours' : ['HTML', 'CSS', 'Bootstrap4'],
}

for(let val in pierre)
{
    
    console.log(`${val} = ${pierre[val]}`);
    
}