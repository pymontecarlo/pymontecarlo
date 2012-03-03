package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.Region;

import java.io.IOException;

import org.jdom.Element;

/**
 * Extractor for the geometry implementation.
 * 
 * @author ppinard
 */
public interface GeometryExtractor extends Extractor {

    /**
     * Extracts the geometry from a XML element.
     * 
     * @param geometryImplElement
     *            XML element
     * @param chamber
     *            region of the chamber as defined in <code>MonteCarloSS</code>
     * @param beamEnergy
     *            beam energy (in joules)
     * @throws IOException
     *             if an error occurs while reading the options
     * @throws EPQException
     *             if an error occurs while setting up the geometry
     * @return surface plane normal
     */
    public double[] extract(Element geometryImplElement, Region chamber,
            double beamEnergy) throws IOException, EPQException;
}
