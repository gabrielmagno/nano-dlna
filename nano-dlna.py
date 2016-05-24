import devices
import streaming
import dlna


if __name__ == "__main__":

    import sys

    device_query = sys.argv[1]
    file_video = sys.argv[2]
    file_subtitle = sys.argv[3]

    files = {"file_video":file_video, "file_subtitle":file_subtitle}
    #files = {"file_video":file_video}
    
    devices = devices.get_devices(5)
    print(devices)

    device = [device for device in devices if device_query in str(device).lower()][0]
    
    target_ip = device["hostname"]
    serve_ip = streaming.get_serve_ip(target_ip)
    files_urls = streaming.start_server(files, serve_ip)
    #files_urls = {key:value.replace("9000", "3000") for key, value in files_urls.items()}
    print(files_urls)

    dlna.play(files_urls, device)

