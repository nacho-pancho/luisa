class user {
  constructor(){
    this.logged=router.app.loggedUsers;
  }
  static isLogged(user){
    return ((typeof this.logged[user])!= "undefined")
  }
}
