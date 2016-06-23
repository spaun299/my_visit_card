function add_my_skill(obj) {
    data = {'name': obj.my_skill.id, 'priority': obj.priority.value,
            'checkbox_value': $('#'+obj.my_skill.id).prop('checked')};

    obj.priority.disabled = (data['checkbox_value']) ? false : true;
    if(data['priority']||!data['checkbox_value']){
    $.ajax({
        url: '/admin/my_skills',
        type: 'post',
        data: data,
        success: function (resp) {
            var color = '#DADFE1';
            if(data['checkbox_value']){
                color = '#1BA39C';}
            obj.priority.parentElement.style.backgroundColor=color;
            obj.priority.parentElement.style.borderColor=color;
        }
    })}
}

add_remove_ip = function (url, add, ip) {
    if(add){
        data = {'add': true, 'ip': document.getElementById('ip').value}
    }
    else{
        data = {'add': false, 'ip': ip}
    }
	$.ajax({
		url: url,
		type: 'post',
		data: data,
		success: function (data) {
			window.location.href = url;
		}
	})
};
