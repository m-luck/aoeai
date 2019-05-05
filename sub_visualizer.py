import logging
import cv2
import os
import numpy as np
import torch
def visualize_features(index,
                       img,
                       pred_features,
                       true_features,
                       savedir,
                       filename):
    logging.info('img.shape = {}'.format(img.shape))
    logging.info('pred_features.shape = {}'.format(pred_features.shape))
    logging.info('true_features.shape = {}'.format(true_features.shape))
    logging.info("Plotting features for batch {} using sample image.".format(index))
    img = img.cpu().detach().numpy()
    img = np.transpose(img, [1, 2, 0])
    logging.info("img max: {:.4f}".format(img.max()))
    all_predicted = torch.sum(pred_features, dim=0)
    all_predicted = all_predicted.cpu().detach().numpy()
    all_actual = torch.sum(true_features, dim=0)
    all_actual = all_actual.cpu().detach().numpy()
    savefile = "{}_features".format(index)
    savefile = os.path.join(savedir, savefile)
    plot1 = plot_with_overlay(img, all_predicted)
    plot2 = plot_with_overlay(img, all_actual)
    save_image(plot1, plot2, savefile)
    logging.info("{:.4f}, {:.4f}".format(all_predicted.max(), all_actual.max()))

def plot_with_overlay(img, overlay):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res = cv2.resize(overlay,dsize=gray_img.shape,interpolation=cv2.INTER_CUBIC)
    fin = cv2.addWeighted(res, 0.95, gray_img, 0.05, 0)
    return fin

def save_image(img1, img2, savefile):
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
    ax1.imshow(img1)
    ax2.imshow(img2)
    fig.savefig(savefile)
plt.close(fig)