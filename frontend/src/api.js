export async function fetchMachines(issues=false){
	const base = 'http://localhost:8000/machines'
	const params = new URLSearchParams()
	if(issues) params.set('issues','true')
	const url = params.toString() ? base + '?' + params.toString() : base
	const res = await fetch(url)
	return await res.json()
}
