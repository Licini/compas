import compas
import os
from compas.datastructures import VolMesh


def test_data():

    if not os.path.exists("temp"):
        os.mkdir("temp")

    vmesh1 = VolMesh.from_obj(compas.get('boxes.obj'))

    data1 = vmesh1.to_data()

    vmesh1.to_json('temp/vmesh1.json')
    vmesh1.from_json('temp/vmesh1.json')

    data1_ = vmesh1.to_data()

    assert data1 == data1_

    vmesh2 = VolMesh.from_data(data1_)

    data2 = vmesh2.to_data()

    vmesh2.to_json('temp/vmesh2.json')
    vmesh2.from_json('temp/vmesh2.json')

    data2_ = vmesh2.to_data()

    assert data2 == data2_

    assert data1 == data2

if __name__ == "__main__":
    test_data()