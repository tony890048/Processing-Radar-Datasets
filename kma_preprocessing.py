import numpy as np
from rasterio.transform import Affine
from pyproj.transformer import Transformer

class RegionTransform(object):
    def __init__(self, source_args, target_args):
        self.source_args = source_args ## width=2305, height=2881, center=(1681,1121), resolution=500
        self.target_args = target_args ## width=256, height=256, resolution=4000
        self.scale_res = self.target_args['resolution'] // self.source_args['resolution']
        self.crs = "+proj=lcc +lat_1=30 +lat_2=60 +lat_0=38 +lon_0=126 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs"

        source_transform = Affine.scale(source_args['resolution'], source_args['resolution']) * Affine.translation(-source_args['center'][1], -source_args['center'][0])
        source_lcc = Transformer.from_crs('EPSG:4326', self.crs)
        def lat_lon_to_index(lat, lon):
            index_col, index_row = source_transform.__invert__().__mul__(source_lcc.transform(lat, lon))
            return np.round(index_col).astype(int), np.round(index_row).astype(int)

        self.x1, self.y1 = lat_lon_to_index(29.0, 120.5)  # (45, -253)
        self.x2, self.y2 = lat_lon_to_index(42.0, 137.5)  # (2959, 2675)

    def __call__(self, img):
        assert img.shape[-2:] == (self.source_args['height'], self.source_args['width'])
        x = img[:self.y2+1, self.x1:]
        x = np.pad(x, ((abs(0-self.y1), 0), (0, abs(self.x2-2305+1))), mode='constant', constant_values=-30000)
        x = np.pad(x, ((0, 7), (21, 0)), mode='constant', constant_values=-30000)   # make it to square -> (2936, 2936)

        # lower resolution & center crop
        x = x[::self.scale_res, ::self.scale_res]
        start_h = (x.shape[0] - self.target_args['height']) // 2
        start_w = (x.shape[1] - self.target_args['width']) // 2
        x = x[start_h:start_h + self.target_args['height'],
            start_w:start_w + self.target_args['width']]
        
        # normalization
        x = np.clip(x, a_min=0., a_max=None) / 10000

        # reverse yaxis (optional)
        x = x[::-1].copy()

        return x
    

if __name__ == "__main__":
    import gzip

    with open('data/kma/RDR_CMP_HSR_PUB_202208082000.bin.gz', mode='rb') as f:
        decompressed_bytes = gzip.decompress(f.read())
        img = np.frombuffer(decompressed_bytes, dtype=np.int16, offset=1024).astype(np.float32).reshape(2881,2305)

    source_args = {'width': 2305, 'height': 2881, 'resolution': 500, 'center': (1681,1121)}
    target_args = {'width': 256, 'height': 256, 'resolution': 4000}

    rt = RegionTransform(source_args, target_args)
    out = rt(img)
    print('output shape: ', out.shape)
    print('output range: ', (out.min(), out.max()))

