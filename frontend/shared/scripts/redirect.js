function redirectToOffer(id){
    if(currentUser){
        window.location.href = "./offer.html?id=" + id;
    } else {
        showToastHint( ["Loggen Sie sich bitte ein, um Details zu sehen."]) 
    }
}

function redirectToOfferList(search){
    if (currentUser == null) {
        showToastHint( ["Loggen Sie sich bitte ein, um Details zu sehen."])
    }
    else {
        if (!search || search.trim().length === 0 ) {
            window.location.href = "./offer_list.html?search=";
        }
        else {
            window.location.href = "./offer_list.html?search=" + search;
        }
    }

}

function redirectToOwnProfile(){
    window.location.href = "./own_profile.html";
}

function redirectToBusinessProfile(id){
    window.location.href = "./business_profile.html?id=" + id;
}

function redirectToCustomerProfile(id){
    window.location.href = "./customer_profile.html?id=" + id;
}

