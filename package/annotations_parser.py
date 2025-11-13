from package.config_loader import get_config
import regex

class AnnotationsParser:
    def __init__(self):
        self.CONFIG = get_config()
        self.pattern = regex.compile(self.CONFIG['unique_id']['pattern'])
        
    def get_location(self, annotations):
        location = ""
        i = 1
        while i < len(annotations):
            annotation = annotations[i]
            text = annotation.description
            if "BLOCK" in text: 
                i += 1
                location += annotations[i].description
                i += 1
                location += annotations[i].description

                return "BLOCK"+location
                # return int(annotations[i+1].description[-1])
            i+=1

        return None
    
    def get_unique_ids(self, annotations):
        unique_ids = []
        is_at = False
        at_coord = None

        def get_center(bbox):
            if not bbox or not bbox.vertices: return None
            xs = [v.x for v in bbox.vertices if hasattr(v, 'x')]
            ys = [v.y for v in bbox.vertices if hasattr(v, 'y')]
            return (sum(xs)/len(xs), sum(ys)/len(ys)) if xs and ys else None

        for annotation in annotations:
            text = annotation.description
            coord = get_center(annotation.bounding_poly)

            # fix l → I and 1 → I
            if len(text)==6 and (text[1]=='l' or text[1]=='1'): text = text[0] + 'I' + text[2:]
            elif len(text)==7 and (text[2]=='l' or text[1]=='1'): text = text[:2] + 'I' + text[3:]

            if text == '@':
                is_at = True
                at_coord = coord
                continue

            if regex.match(self.pattern, text):   # normal IDs
                unique_ids.append((text, coord))

            if is_at:  # case: '@' + text
                combined = '@' + text
                if regex.match(self.pattern, combined):
                    # pick average of @ and ID coordinate if both exist
                    if at_coord and coord:
                        coord = ((at_coord[0]+coord[0])/2, (at_coord[1]+coord[1])/2)
                    else:
                        coord = at_coord or coord
                    unique_ids.append((combined, coord))
                is_at = False

        return unique_ids
