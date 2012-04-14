package pymontecarlo.program.nistmonte.input;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.Utility.Histogram;

import java.io.IOException;
import java.io.StringWriter;
import java.util.Properties;
import java.util.zip.ZipOutputStream;

import ptpshared.opencsv.CSVWriter;
import pymontecarlo.util.ZipUtil;

/**
 * Abstract detector to collect data in a number of channels between two limits.
 * 
 * @author ppinard
 */
public abstract class AbstractChannelDetector extends
        AbstractScatteringDetector implements ChannelDetector {

    /** Histogram to store the data. */
    protected final Histogram histogram;



    @Override
    public void reset() {
        super.reset();
        histogram.clear();
    }



    /**
     * Creates a new <code>AbstractChannelDetector</code>.
     * 
     * @param min
     *            lower limit of the detector
     * @param max
     *            upper limit of the detector
     * @param channels
     *            number of channels (bins)
     */
    public AbstractChannelDetector(double min, double max, int channels) {
        if (channels <= 0)
            throw new IllegalArgumentException(
                    "Number of channels must be greater than 0");

        min = Math.min(min, max);
        max = Math.max(min, max);
        histogram = new Histogram(min, max, channels);
    }



    @Override
    public void setup(MonteCarloSS mcss) throws EPQException {
        mcss.addActionListener(this);
    }



    /**
     * Returns the header of the bins column.
     * 
     * @return header of the bins column
     */
    public abstract String getBinsHeader();



    /**
     * Returns the header of the counts column.
     * 
     * @return header of the counts column
     */
    public String getCountsHeader() {
        return "Counts";
    }



    @Override
    public void saveResults(ZipOutputStream zipOutput, String key)
            throws IOException {
        // Create CSV
        StringWriter sw = new StringWriter();
        CSVWriter writer = new CSVWriter(sw);

        writer.writeNext(getBinsHeader(), getCountsHeader());

        double x, y;
        for (int i = 0; i < histogram.binCount(); i++) {
            x = (histogram.minValue(i) + histogram.maxValue(i)) / 2.0;
            y = histogram.counts(i);

            writer.writeNext(x, y);
        }

        writer.close();

        // Save CSV in ZIP
        ZipUtil.saveStringBuffer(zipOutput, key + ".csv", sw.getBuffer());
    }



    @Override
    protected void saveAsProperties(Properties props) {
        super.saveAsProperties(props);

        props.setProperty("histogram.min", Double.toString(getMinimumLimit()));
        props.setProperty("histogram.max", Double.toString(getMaximumLimit()));
        props.setProperty("histogram.channels",
                Integer.toString(histogram.binCount()));
    }



    @Override
    public double getMinimumLimit() {
        return histogram.minValue(0);
    }



    @Override
    public double getMaximumLimit() {
        return histogram.maxValue(histogram.binCount() - 1);
    }



    @Override
    public double getChannelWidth() {
        return histogram.maxValue(0) - histogram.minValue(0);
    }



    @Override
    public int getChannels() {
        return histogram.binCount();
    }

}
