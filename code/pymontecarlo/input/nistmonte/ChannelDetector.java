package pymontecarlo.input.nistmonte;

/**
 * Detector consisting of a number of channels between two limits.
 * 
 * @author ppinard
 */
public interface ChannelDetector {

    /**
     * Returns the lower limit of this distribution.
     * 
     * @return lower limit
     */
    public double getMinimumLimit();



    /**
     * Returns the upper limit of this distribution.
     * 
     * @return upper limit
     */
    public double getMaximumLimit();



    /**
     * Returns the number of channels of this distribution.
     * 
     * @return number of channels
     */
    public int getChannels();



    /**
     * Returns the width of one channel.
     * 
     * @return width of one channel
     */
    public double getChannelWidth();
}
