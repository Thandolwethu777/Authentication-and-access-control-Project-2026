"use strict";
const role = document.querySelector('main').dataset.role;
const sources = role === 'admin' ? {
  students:'/admin/students', lecturers:'/admin/lecturers', courses:'/admin/courses',
  enrolments:'/admin/enrolments', grades:'/admin/grades'
} : {courses:'/lecturer/courses', students:'/lecturer/students', grades:'/lecturer/grades'};
const columns = {
  students:[['student_number','Student number'],['first_name','First name'],['last_name','Last name'],['email','Email']],
  lecturers:[['lecturer_id','ID'],['first_name','First name'],['last_name','Last name'],['email','Email'],['department','Department']],
  courses:[['course_code','Code'],['course_name','Course name']],
  enrolments:[['student_number','Student'],['course_code','Course'],['enrolment_date','Date']],
  grades:[['student_number','Student'],['course_code','Course'],['grade','Grade']]
};
async function loadSection(key) {
  const target = document.getElementById('table-'+key);
  target.replaceChildren();
  const status=document.createElement('div'); status.className='state'; status.textContent='Loading...'; target.append(status);
  try {
    const response=await fetch(sources[key],{credentials:'same-origin'});
    if(response.status===401){location.replace('/');return;}
    const data=await response.json();
    if(!response.ok) throw new Error(data.error || 'Request failed');
    if(!Array.isArray(data)) throw new Error('Unexpected server response');
    if(!data.length){status.textContent='No records available.';return;}
    const table=document.createElement('table'), head=document.createElement('thead'), tr=document.createElement('tr');
    for(const [,label] of columns[key]){const th=document.createElement('th');th.textContent=label;tr.append(th);}
    head.append(tr);table.append(head);
    const body=document.createElement('tbody');
    for(const record of data){const row=document.createElement('tr');for(const [field] of columns[key]){
      const td=document.createElement('td');td.textContent=record[field] == null ? '—' : String(record[field]);row.append(td);
    }body.append(row);}table.append(body);target.replaceChildren(table);
  }catch(error){status.className='state error';status.textContent=error.message;}
}
function showView(key){
  document.querySelectorAll('.view').forEach(el=>el.classList.toggle('active',el.id===key));
  document.querySelectorAll('[data-view]').forEach(el=>el.classList.toggle('active',el.dataset.view===key));
  loadSection(key);
}
document.querySelectorAll('[data-view]').forEach(el=>el.addEventListener('click',()=>showView(el.dataset.view)));
document.querySelectorAll('[data-go]').forEach(el=>el.addEventListener('click',()=>showView(el.dataset.go)));
document.getElementById('logoutButton').addEventListener('click',async()=>{
  try{await fetch('/logout',{method:'POST',credentials:'same-origin'});}finally{location.replace('/');}
});
fetch('/session-info').then(r=>r.ok?r.json():Promise.reject()).then(data=>{
  if(data.app_role!==role){location.replace('/');return;}
  loadSection(Object.keys(sources)[0]);
}).catch(()=>location.replace('/'));
