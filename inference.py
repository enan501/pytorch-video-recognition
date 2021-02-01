import torch
import numpy as np
from vmz.models import r2plus1d_34
import cv2
from PIL import Image
torch.backends.cudnn.benchmark = True

default_path = '/Users/enan/Projects/2020-02/grad-project/pytorch-video-recognition/dataset/'
video = default_path + 'head/15_subject002_webcam_abnormal_2.mp4'


def center_crop(frame):
    frame = frame[8:120, 30:142, :]
    return np.array(frame).astype(np.uint8)


def main():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("Device being used:", device)

    # with open('./dataloaders/ucf_labels.txt', 'r') as f:
    #    class_names = f.readlines()
    #    f.close()
    # init model
    model = r2plus1d_34(pretraining="kinetics_8frms")
    model.to(device)
    model.eval()

    # read video

    cap = cv2.VideoCapture(video)
    retaining = True

    clip = []
    while retaining:
        retaining, frame = cap.read()
        if not retaining and frame is None:
            continue
        tmp_ = center_crop(cv2.resize(frame, (171, 128)))
        tmp = tmp_ - np.array([[[90.0, 98.0, 102.0]]])
        clip.append(tmp)
        if len(clip) == 8:
            inputs = np.array(clip).astype(np.float32)
            inputs = np.expand_dims(inputs, axis=0)
            inputs = np.transpose(inputs, (0, 4, 1, 2, 3))
            inputs = torch.from_numpy(inputs)
            inputs = torch.autograd.Variable(inputs, requires_grad=False).to(device)
            with torch.no_grad():
                outputs = model.forward(inputs)

            probs = torch.nn.Softmax(dim=1)(outputs)
            label = torch.max(probs, 1)[1].detach().cpu().numpy()[0]

            # cv2.putText(frame, class_names[label].split(' ')[-1].strip(), (20, 20),
            cv2.putText(frame, str(label), (20, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 0, 255), 1)
            cv2.putText(frame, "prob: %.4f" % probs[0][label], (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 0, 255), 1)
            clip.pop(0)

        Image.fromarray(frame,'RGB').show()
        # cv2.imshow('result', frame)
        # cv2.waitKey(30)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()