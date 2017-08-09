function data = zmq_recv(socket)

    while (1)
        data = py.pyzmq.recv(socket); % do not freeze
        if strcmp(class(data), 'py.str')
            data = typecast(uint8(data) ,'double');
            break;
        end
        pause(0.001);
    end
end
