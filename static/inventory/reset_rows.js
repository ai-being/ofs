// SWAMI KARUPPASWAMI THUNNAI

function reset_rows()
{
	let elements = document.getElementsByClassName("table_elements");
	for(let i=0; i< elements.length; i++)
	{
		elements[i].value = i+1;
	}
}