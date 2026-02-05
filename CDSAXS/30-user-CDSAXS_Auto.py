
def test():
    yield from bp.count([OAV_writing,piezo]) 

def scan_pushpin(xmin, xmax, xinc, zmin, zmax, zinc, prsmin, prsmax, prsnumpoints):
   """
   Rotation center alignment
   General Procedure:
   - Scan over  piezo.x, piezo.z and PRS stage
   - Save OAV and top down images current
  
   Motors:
   - piezo.x
   - piezo.z
   - prs
   """
   sample_id(user_name="pw",sample_name=f"test000_{get_scan_md()}")
   #    import numpy as np 
   xpos = np.arange(xmin,xmax+xinc,xinc)
   zpos = np.arange(zmin,zmax+zinc,zinc)
   prspos = np.linspace(prsmin,prsmax,prsnumpoints)


   P,X,Z=np.meshgrid(prspos,xpos,zpos)
   X,Z,P=X.flatten(),Z.flatten(),P.flatten()
   yield from bp.list_scan([OAV_writing,OAV2_writing, piezo, prs],piezo.x,X,piezo.z,Z, prs,P)

#def scan_pushpin(xmin, xmax, xinc, zmin, zmax, zinc, prsmin, prsmax, prsnumpoints)

# rel_grid_scan([OAV_writing,OAV2_writing, piezo, prs],
#               prs, -60, 60, 5,
#               piezo.x, -500, 500, 11,
#               piezo.z, -500, 500, 11,
#               snake_axes=True)

# 2026-01-30 
# # Aligned pushpin x -3625, z 4374

### Preprocessing images for VLM Analysis

def preprocess_image_tiled(tmp_path, coord_idx_lookup, images, prs_list, scan_id, x, z):
    
    print("running preprocess_image_tiled")
    grays = []
    for prs in prs_list:
        key = f"[{x}, {z}, {prs}]"
        if key not in coord_idx_lookup.keys():
            continue
        img = np.array(images[coord_idx_lookup[key]][0])
        gray = np.dot(img[..., :3], [0.2989, 0.5870, 0.1140])
        grays.append(gray)

    
    np.array(grays)
    mean_gray = np.mean(grays, axis = 0)
    print(os.path.join(tmp_path, f'samx{x:.0f}_z{z:.0f}_complete_angles_superimposed_cropped.png'))
    cv2.imwrite(os.path.join(tmp_path, f'samx{x:.0f}_z{z:.0f}_complete_angles_superimposed_cropped.png'), mean_gray)

    # Normalize to uint8 for Enhancement
    mean_gray_u8 = cv2.normalize(mean_gray, None, 0, 255, cv2.NORM_MINMAX)
    mean_gray_u8 = mean_gray_u8.astype(np.uint8)
    clip_limit = 5.0    
    tile_grid = (16,16)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid)
    enh = clahe.apply(mean_gray_u8)
    enh_img_path = os.path.join(tmp_path, f'samx{x:.0f}_z{z:.0f}_complete_angles_superimposed_enh_cropped.png')
    cv2.imwrite(enh_img_path, enh)
    print(enh_img_path)
    print("The superimposed images are captured for coordinate: ", [x,z])

#### VLM functions

# Initialize the Anthropic client
# anthropic_client
# Initialize Azure OpenAI client


def load_system_prompt(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")

def analyze_multiple_images_with_thinking(
    image_paths: list[str],  # Changed to list of paths
    user_query: str,
    prompt_file: str = None,
    model_id: str = "claude-opus-4-1-20250805",
    thinking_budget: int = 10000,
    max_tokens: int = 32000
) -> dict:
    """Analyze multiple images with extended thinking using streaming."""
    
    # Build content array with multiple images
    content = []
    print("......")
    # Add all images first
    for i, image_path in enumerate(image_paths):
        image_data, media_type = encode_image(image_path)
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data,
            }
        })
        content.append({"type": "text", "text": f"Image {i+1}"})  # Optional label for each image
    
    with open("content.json", "w") as f:
        json.dump(content, f, indent=4)
    # Add the text query at the end
    content.append({"type": "text", "text": user_query})

    # print(content)
    thinking_content = ""
    final_response = ""
    
    # Optional: load system prompt
    system_prompt = None
    if prompt_file:
        system_prompt = load_system_prompt(prompt_file)
    
    # Build request kwargs
    request_kwargs = {
        "model": model_id,
        "max_tokens": max_tokens,
        "thinking": {
            "type": "enabled",
            "budget_tokens": thinking_budget
        },
        "messages": [
            {
                "role": "user",
                "content": content,
            }
        ],
    }
    
    if system_prompt:
        request_kwargs["system"] = system_prompt
    
    # Use streaming for long operations
    with anthropic_client.messages.stream(**request_kwargs) as stream:
        for event in stream:
            if event.type == "content_block_start":
                if hasattr(event.content_block, "type"):
                    if event.content_block.type == "thinking":
                        thinking_content = ""
                    elif event.content_block.type == "text":
                        final_response = ""
            
            elif event.type == "content_block_delta":
                if hasattr(event.delta, "thinking"):
                    thinking_content += event.delta.thinking
                elif hasattr(event.delta, "text"):
                    final_response += event.delta.text
    
    return {
        "thinking": thinking_content,
        "response": final_response
    }

# Streaming version for long operations
def analyze_images_azure_streaming(
    image_paths: list[str],
    user_query: str,
    prompt_file: str = None,
    deployment_name: str = "gpt-4o"
) -> str:

    messages = []

    if prompt_file:
        system_prompt = load_system_prompt(prompt_file)
        messages.append({"role": "system", "content": system_prompt})

    # Single user message with images + text
    user_content = []
                
    # Add all images to analyze
    for i, image_path in enumerate(image_paths):
        image_data, media_type = encode_image(image_path)
        user_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{media_type};base64,{image_data}",
                "detail": "high"
            }
        })
        user_content.append({
            "type": "text",
            "text": f"ImageID = {i}"
        })

    # Add query LAST
    user_content.append({
        "type": "text",
        "text": user_query
    })

    messages.append({
        "role": "user",
        "content": user_content
    })

    response_text = ""
    stream = gpt_client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        # max_tokens=4096,
        # temperature=0,
        stream=True
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content

    return response_text


def analyze_images_abacus_streaming(
    image_paths: list[str],
    user_query: str,
    prompt_file: str = None,
    model: str = "gemini-3-pro"
) -> str:
    # optional system prompt
    system_prompt = load_system_prompt(prompt_file) if prompt_file else None

    # Build multimodal message content: images + labels + query
    user_content = []
    for i, image_path in enumerate(image_paths):
        image_data, media_type = encode_image(image_path)
        user_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{media_type};base64,{image_data}",
                "detail": "high",
            },
        })
        user_content.append({"type": "text", "text": f"ImageID = {i}"})  # ensure string

    # Put the actual question as text content (string)
    user_content.append({"type": "text", "text": str(user_query)})

    messages = [{"role": "user", "content": user_content}]

    # IMPORTANT: prompt must be a string (or just omit it)
    resp = abacus_client.evaluate_prompt(
        # prompt="",  # or prompt=str(user_query) and remove the last user_content append
        messages=messages,
        system_message=system_prompt,
        llm_name=model,
    )

    # Abacus returns an object with .content
    return resp.content if hasattr(resp, "content") else str(resp)

def best_coordinate_tiled(
        x_coords: list[float],
        z_coords: list[float],
        # current_coord: list[float], ## [x-coordinate, z-coordinate]
        tmp_path: str,
        model: str = "claude-opus-4-5-20251101",
        ):

    # x_vals = [current_coord[0] - step_size, current_coord[0], current_coord[0] + step_size]
    # z_vals = [current_coord[1] + step_size, current_coord[1], current_coord[1] - step_size]

    coord_list = []
    image_paths = []
    for z in z_coords:
        for x in x_coords:
            if x_coords[0] <= x <= x_coords[-1] and z_coords[-1] <= z <= z_coords[0]:
                coord_list.append([x,z])
                print(os.path.join(tmp_path, f"samx{x:.0f}_z{z:.0f}_complete_angles_superimposed_enh_cropped.png"))
                image_paths.append(os.path.join(tmp_path, f"samx{x:.0f}_z{z:.0f}_complete_angles_superimposed_enh_cropped.png"))

    if model in anthropic_models:
        # For Anthorpic models
        print("...")
        print("Analyzing with model:", model)
        result = analyze_multiple_images_with_thinking(
            image_paths=image_paths,
            # image_paths=image_paths[2:-2],
            model_id= model,
            user_query="""Rank these superimposed images in terms of better needle alignment.""",
            prompt_file="/home/xf12id/SWAXS_user_scripts/CDSAXS/local_ranking/sys_prompt_all_angles_superimposed_ranking.md",
            thinking_budget=15000  # Increase for multiple images
        )

        # print("Model Response:", result["response"])
        result_json = parse_json_with_retry(result["response"], max_retries=3, timeout=2)
        print(result_json)
        if "image" in result_json["Rank-1"].lower():
            best_coord_idx = int(result_json["Rank-1"].split(" ")[1]) - 1
        else:
            best_coord_idx = int(result_json["Rank-1"]) - 1

    elif model in gpt_models:
        ## For Azure OpenAI models
        print("Analyzing with model:", model)
        result = analyze_images_azure_streaming(
            image_paths = image_paths,
            user_query = "Rank these superimposed images in terms of better needle alignment.",
            prompt_file="/home/xf12id/SWAXS_user_scripts/CDSAXS/local_ranking/sys_prompt_all_angles_superimposed_ranking.md",
            deployment_name=model,  # Your Azure deployment name
        )
        # print("Model Response:", result)
        if "```json" in result:
            result_json = parse_json_with_retry(result, max_retries=3, timeout=2)
        else:
            result_json = json.loads(result)
        print(result_json)
        if "image" in result_json["Rank-1"].lower():
            best_coord_idx = int(result_json["Rank-1"].split(" ")[1]) - 1
        else:
            best_coord_idx = int(result_json["Rank-1"]) - 1
    else:
        ## For Gemini models
        print("Analyzing with model:", model)
        
        result = analyze_images_abacus_streaming(
            image_paths = image_paths,
            user_query = "Rank these superimposed images in terms of better needle alignment.",
            prompt_file="/home/xf12id/SWAXS_user_scripts/CDSAXS/local_ranking/sys_prompt_all_angles_superimposed_ranking.md",
            model=model)
        # print("Model response:", result)
        if "```json" in result:
            result_json = parse_json_with_retry(result, max_retries=3, timeout=2)
        else:
            result_json = json.loads(result)
        print(result_json)
        # if "image" in result_json["Rank-1"].lower():
        #     best_coord_idx = int(result_json["Rank-1"].split(" ")[1]) - 1
        # else:
        best_coord_idx = int(result_json["Rank-1"])

    print(coord_list)
    return coord_list[best_coord_idx]


def auto():

    if 1:
        # print("The best coordinate is: ", best_coord)

        ##### Run a scan 
        # yield from rel_grid_scan([OAV_writing, OAV2_writing, piezo, prs],
        #         prs, -60, 60, 5,
        #         piezo.x, -50, 50, 3,
        #         piezo.z, -50, 50, 3,
        #         snake_axes=True)


        scan_id = -1
        # step_size = 100.00
        ##### Grab the scan results (camera image)
        x = db.v2[scan_id]['primary']['data']['piezo_x'].read()
        z = db.v2[scan_id]['primary']['data']['piezo_z'].read()
        phi = db.v2[scan_id]['primary']['data']['prs'].read()
        imgs = db.v2[scan_id]['primary']['data']['OAV_writing_image'].read()
        # img[0][0]

        ##### Pre-processing for VLM
        ## Capture the x-coords from the scan
        x_array = np.array(x[:])
        x_coords = sorted(list(set(x_array.tolist()))) ## In increasing order

        ## Capture the z-coords from the scan
        z_array = np.array(z[:])
        z_coords = sorted(list(set(z_array.tolist())))[::-1] ## In decreasing order

        ## Capture the prs from the scan
        prs_array = np.array(phi[:])
        prs_values = sorted(list(set(prs_array.tolist()))) ## In increasing order

        ## Create a Hashmap for the {[x,z,prs] : index of the image}
        coord_idx_lookup = {}
        for i in range(x_array.shape[0]):
            coord_idx_lookup[f"[{x_array[i]}, {z_array[i]}, {prs_array[i]}]"] = i
        
        tmp_path = "/home/xf12id/SWAXS_user_scripts/CDSAXS/local_ranking/tmp2"

        ## Preprocess the scanned images and store them to the tmp folder. Storing is done for the evaluation purposes. 
        for x_val in x_coords:
            for z_val in z_coords:
                print("path we are looking for: ", os.path.join(tmp_path, f"samx{x_val:.0f}_z{z_val:.0f}_complete_angles_superimposed_cropped.png"))
                # if os.path.exists(os.path.join(tmp_path, f"samx{x_val:.0f}_z{z_val:.0f}_complete_angles_superimposed_cropped.png")):
                #     continue
                preprocess_image_tiled(tmp_path = tmp_path, coord_idx_lookup=coord_idx_lookup, images = imgs, prs_list=prs_values, scan_id=scan_id, x=x_val, z=z_val)
        
        ##### Processing/VLM, input is (x, z, img), return (suggest_x, suggest_z) positions
        ## Running the Ranking based algorithm using VLMs to capture the best coordinate staring from the top-left corner of the scan

        steps = 10
        # x_lower_limit = x_coords[0]
        # x_upper_limit = x_coords[-1]
        # z_lower_limit = z_coords[-1]
        # z_upper_limit = z_coords[0]
        curr_coord = [x_coords[0], z_coords[0]]
        # step_size = step_size
        print("######")
        print("Starting from the current coordinate: ", curr_coord)
        best_coords_list = [curr_coord]
        for i in range(steps):
            best_coord = best_coordinate_tiled(
                x_coords = x_coords,
                z_coords = z_coords,
                # current_coord = curr_coord, ## [x-coordinate, z-coordinate]
                tmp_path = tmp_path, ## To store the preprocessed images
                # step_size = step_size,
                model= "claude-opus-4-5-20251101")
            print(f"For iteration-{i+1} best coordinate is: ", best_coord)

            best_coords_list.append(best_coord)
            if best_coords_list.count(best_coord) >= 3:
                break
            curr_coord = best_coord

        print("The best coordinate is: ", best_coord)

        time.sleep(5)

        ##### Move the sample motor (Careful, this moves the physical motors at beamline)
        # suggest_x = x+10  #for testing only
        # suggest_z = z+10
        suggest_x = best_coord[0]
        suggest_z = best_coord[1]
        yield from bps.mv(piezo.x, suggest_x)
        yield from bps.mv(piezo.z, suggest_z)




