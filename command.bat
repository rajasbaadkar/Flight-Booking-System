start cmd /k "python loadbalancer.py"
timeout 2
start cmd /k "python server1.py"
start cmd /k "python server2.py"
start cmd /k "python server3.py"
start cmd /k "python server4.py"
timeout 2
start cmd /k "python client.py"
start cmd /k "python client.py"
@REM start cmd /k "python client.py"
@REM start cmd /k "python client.py"
@REM start cmd /k "python client.py"