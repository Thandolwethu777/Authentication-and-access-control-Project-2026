"use strict";
const role = document.querySelector('main').dataset.role;
const sources = role === 'admin' ? {
  students:'/admin/students', lecturers:'/admin/lecturers', courses:'/admin/courses',
  enrolments:'/admin/enrolments', grades:'/admin/grades'
} : role === 'student' ? {courses:'/my-courses', grades:'/my-grades', enrolments:'/my-enrolments'} : {courses:'/lecturer/courses', students:'/lecturer/students', grades:'/lecturer/grades'};
const columns = {
  students:[['student_number','Student number'],['first_name','First name'],['last_name','Last name'],['email','Email']],
  lecturers:[['lecturer_id','ID'],['first_name','First name'],['last_name','Last name'],['email','Email'],['department','Department']],
  courses:[['course_code','Code'],['course_name','Course name']],
  enrolments:[['student_number','Student'],['course_code','Course'],['enrolment_date','Date']],
  grades:[['student_number','Student'],['course_code','Course'],['course_name','Course name'],['grade','Grade']]
};
function gradeEditor(record) {
  const cell = document.createElement('td');
  const form = document.createElement('form');
  const input = document.createElement('input');
  input.type = 'number';
  input.min = '0';
  input.max = '100';
  input.step = '0.01';
  input.required = true;
  input.value = record.grade ?? '';
  input.setAttribute('aria-label', 'Grade for ' + record.student_number + ' in ' + record.course_code);
  const button = document.createElement('button');
  button.textContent = 'Save';
  const message = document.createElement('span');
  message.setAttribute('role', 'status');
  form.append(input, button, message);
  cell.append(form);
  form.addEventListener('submit', async event => {
    event.preventDefault();
    button.disabled = true;
    message.textContent = '';
    try {
      const response = await fetch('/admin/grades/' + record.grade_id, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({grade: input.value})
      });
      if (response.status === 401) { location.replace('/'); return; }
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Could not save grade');
      input.value = result.grade;
      message.textContent = 'Saved';
    } catch (error) {
      message.textContent = error.message;
    } finally {
      button.disabled = false;
    }
  });
  return cell;
}
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
      if (role === 'admin' && key === 'grades' && field === 'grade') { row.append(gradeEditor(record)); continue; }
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
document.getElementById('logoutButton').addEventListener('click',async event=>{
  event.preventDefault();
  try {
    const response = await fetch('/logout',{method:'POST',credentials:'same-origin'});
    if (!response.ok) throw new Error();
    location.replace('/');
  } catch { alert('Sign out failed. Please try again.'); }
});
fetch('/session-info').then(r=>r.ok?r.json():Promise.reject()).then(data=>{
  if(data.app_role!==role){location.replace('/');return;}
  document.querySelector('.userlabel').textContent = [data.first_name, data.last_name].filter(Boolean).join(' ') || data.username;
  loadSection(Object.keys(sources)[0]);
}).catch(()=>location.replace('/'));
