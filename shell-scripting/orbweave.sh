#!/bin/sh
# purpose: commands for easily interacting with an on-demand ec2 instance (starting, stopping, status checking, ssh)

base_wait=3
base_iters=10


# dummy function for convenience with local machine aliasing 
launch () {
    echo 
    echo "hello! shall we awaken the Orbweaver?  🕷  🕸  🔮"
    echo
}


# loads the instance and security group ID from configuration file. 
# default path for my local machine, filepath can be added as positional variable alternatively.
load_ids () {
    if [ -z ${1+x} ]; 
    then 
        default="/Documents/GitHub/play/"
        fp="./$default/config_ow.sh"

    else 
        fp="$1/config_ow.sh"
    fi
    
    source $fp
    }


# removes quotes in aws outputs 
strip () {
    v=@
    stripped="${@%\"}"
    stripped="${stripped#\"}"
    echo $stripped
}


# get instance ip generated for current session 
get_ip () {
    o=$(aws ec2 describe-instances --instance-ids $instance_id --output json)
    ip_=$(echo $o | jq ".Reservations[].Instances[].PublicIpAddress")
    ip_=$(strip $ip_)
    echo $ip_
}


# check status of instance 
check_status () {
    o=$(aws ec2 describe-instances \
        --instance-ids $instance_id \
        --output json)
    status_=$(echo $o | jq ".Reservations[].Instances[].State.Name")
    status_=$(strip $status_)
    echo $status_
}


# alias
check () {
    check_status
}


# alias
status () {
    check_status
}


# starts the instance 
start () {
    o=$(aws ec2 start-instances \
        --instance-ids $instance_id \
        --query 'StartingInstances[0]'.CurrentState.Name
        )
    o=$(strip $o)
    echo "process: $o"

    # --track will confirm startup
    if [[ "$*" == *"--track"* ]];
    then
        i=0
        while [ "$i" -lt $base_iters ] && [ "$status_" != "running" ];
        do
            echo "current status: $status_"
            i=$(( i + 1 ))
            sleep $base_wait
            status_=$(check_status)
        done 

        echo "...it's alive!  🕷  🧟‍♀️"
    fi 
}


# stops the instance 
stop () {
    # TODO load_ids (at least if the variables are unset)

    o=$(aws ec2 stop-instances \
        --instance-ids $instance_id \
        --query 'StoppingInstances[0]'.CurrentState.Name
        )
    o=$(strip $o)
    echo "process: $o"

    # --track option will confirm shutdown 
    if [[ "$*" == *"--track"* ]];
    then
        i=0
        iters=$(( $base_iters*2 ))
        while [ "$i" -lt $iters ] && [ "$status_" != "stopped" ];
        do
            echo "current status: $status_"
            i=$(( i + 1 ))
            sleep $(( $base_wait*2 ))
            status_=$(check_status)
        done 

        echo "shh... Orbweaver is sleeping now  😴  🕷"
    fi
}


# ssh
tunnel () {
    ip_=$(get_ip) # null is a string here. getting this right was touchy. 
    if [ "$ip_" = "null" ]; 
    then
        echo "no IP address detected for Orbweaver. confirm that instance is running with orbweave check_status"
    else 
        echo "tunneling into Orbweaver IP: $ip_"
        # -o term will automatically apply fingerprint, making authentication easier
        # -L term allows jupyter notebook access with url localhost:8888
        ssh -o StrictHostKeyChecking=accept-new \
            -L localhost:8888:localhost:8888 ubuntu@$ip_
    fi
}


# return true if local ip address is already in security group 
check_my_ip () {
    my_ip=$(curl ifconfig.me)

    approved_ips=$(
        aws ec2 describe-security-group-rules \
        --filter Name="group-id",Values=$security_group_id \
        --query 'SecurityGroupRules[*]'.CidrIpv4 \
        --output json 
        )
        # generates the list of approved IPs as a JSON array

    echo $approved_ips | jq "contains([\"$my_ip\"])" 

}


# add local ip to the security group 
add_my_ip () {
    my_ip=$(curl ifconfig.me)

    # variable assignment to keep it quiet 
    o=$(aws ec2 authorize-security-group-ingress \
        --group-id $security_group_id \
        --protocol tcp \
        --port 22 \
        --cidr $my_ip/32)
}


# master function, should always be able to run this to get in
excavate () {
    load_ids $1 # can pass an alternative path

    start --confirm

    if [ $(check_my_ip) = "false" ]; then
        echo "adding local IPv4 to security group"
        add_my_ip
    fi

    # TODO while statement for get_ip_ until it returns != null
    echo "giving Orbweaver time to start..."
    sleep $(( $base_wait*2 ))

    tunnel
}


help () {
   # display help 
    echo
    echo "Orbweaver is my nickname for a cloud computer (GPU) that exists \
to create rapid deep neural networks and catch answers in its web 🕷  🕸  🔮"
    echo "this shell script exists as a simple way to interact with Orbweaver: \
starting, stopping, and secure shell tunneling into the instance, for example."
    echo
    echo "here's how to start orbweaving:"
    echo "syntax: orbweave [function]"
    echo "commands:"
    echo "  add_my_ip        add the current local ip to the security \
group (required on first connection from a new secure local ip)"
    echo "  check_my_ip      determine whether the current local ip is \
in the security group. returns boolean"
    echo "  check_status     returns the status of the cloud computer \
instance. succint aliases are check and status"
    echo "  excavate         a full-process function that can be used 
singly to handle permissions and ssh into the instance. starts the ec2 \
instance, adds local ip to security group if needed, and ssh in"
    echo "  get_ip           get and store the current Public IPv4 of \
the cloud computer"
    echo "  help             this printout, how meta..."
    echo "  launch           a cute dummy function"
    echo "  load_ids         get the instance id and other variables \
from the 'config_ow.sh' configuration file (instance_id, security_group_id)"
    echo "  start            start the cloud computer. pass --track \
to confirm startup."
    echo "  stop             stop the cloud computer. pass --track \
to confirm shutdown."
    echo "  tunnel           run get_ip then secure shell into the \
cloud computer with this ip"
    echo "requirements:"
    echo " the local machine running orbweave.sh should have aws cli \
already configured and authenticated."
    echo
    echo "process:"
    echo "  prerequisite: you must have configured the aws cli on your machine with credentials authenticated \
for the instance you are trying to interact with."
    echo "  excavate can always be run to handle all permissions and commands needed for ssh."
    echo "  stop can be used when you are done with the instance. using stop --track will confirm whether instance properly shuts down, without needing to check_status afterwards"
    echo
    echo "    ~~~~ happy computing! stay spooky! ~~~~"
    echo 

}