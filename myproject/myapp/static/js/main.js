/*=============== SHOW HIDDEN - PASSWORD ===============*/
window.onload = function(){

   const showHiddenPass = (id_password, loginEye) =>{
      const input = document.getElementById(id_password)
      const iconEye = document.getElementById(loginEye)
   
      iconEye.addEventListener('click', () =>{
         // Change password to text
         if(input.type === 'password'){
            // Switch to text
            input.type = 'text'
   
            // Icon change
            iconEye.classList.add('ri-eye-line')
            iconEye.classList.remove('ri-eye-off-line')
         } else{
            // Change to password
            input.type = 'password'
   
            // Icon change
            iconEye.classList.remove('ri-eye-line')
            iconEye.classList.add('ri-eye-off-line')
         }
      })
   }
   
  showHiddenPass('id_password','login-eye')

}
