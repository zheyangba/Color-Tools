def parse_mask_to_coco(image_id, anno_id, image_mask, category_id, poly=False):
    start_anno_id = anno_id
    x, y, width, height = bounding_box_from_mask(image_mask)
    if poly == False:
        fortran_binary_mask = np.asfortranarray(image_mask)
        encoded_mask = mask.encode(fortran_binary_mask)
    if poly == True:
        contours = measure.find_contours(image_mask, 0.5)
    annotation = {
        "id": start_anno_id,
        "image_id": image_id,
        "category_id": category_id,
        "bbox": [float(x), float(y), float(width), float(height)],
        "area": float(width * height),
        "iscrowd": 0,
        "segmentation": [],
    }
    if poly == False:
        annotation["segmentation"] = encoded_mask
        annotation["segmentation"]["counts"] = str(
            annotation["segmentation"]["counts"], "utf-8"
        )
    if poly == True:
        for contour in contours:
            contour = np.flip(contour, axis=1)
            segmentation = contour.ravel().tolist()
            sc = bunch_coords(segmentation)
            sc = simplify_coords_vwp(sc, 2)
            sc = unbunch_coords(sc)
            annotation["segmentation"].append(sc)
    return annotation


def bounding_box_from_mask(mask):
    mask = mask.astype(np.uint8)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    all_contours = []
    for contour in contours:
        all_contours.extend(contour)
    convex_hull = cv2.convexHull(np.array(all_contours))
    x, y, w, h = cv2.boundingRect(convex_hull)
    return x, y, w, h